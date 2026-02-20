import psutil
import time
import contextlib
import os
import logging
import random
import msvcrt 
from collections import deque
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import box
from scamp import Session

# ==========================================
# 0. 로그 차단
# ==========================================
for logger_name in ["root", "clockblocks", "scamp"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    from scamp import Session

console = Console()
console.print("[bold yellow]Initializing Audio Engine... (6-Core Ensemble)[/bold yellow]")

s = Session(max_threads=1000)

# ==========================================
# 악기 설정 (6개 파트)
# ==========================================

# 1. Guitar Lead (Melody) - Core 0
guitar_lead = s.new_part("Electric Guitar (jazz)")

# 2. Guitar Chord (Rhythm) - Core 2
guitar_chord = s.new_part("Electric Guitar (clean)")

# 3. Keys Lead (Counter Melody) - Core 4
keys_lead = s.new_part("Clavinet")

# 4. Keys Chord (Comping/Pad) - Core 6
keys_chord = s.new_part("Electric Piano 1")

# 5. Drums - Core 8
drum_kit = s.new_part("Standard Drum Kit")

# 6. Bass - Core 10
bass_guitar = s.new_part("Electric Bass (pick)")

TARGET_CORES = [0, 2, 4, 6, 8, 10]

# ==========================================
# 2. 음악 데이터
# ==========================================
SCALE_NOTES = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]

CHORD_LEVELS = [
    ("Idle",   "C Maj7", [60, 64, 67, 71]),
    ("Light",  "F Maj7", [53, 57, 60, 64]),
    ("Work",   "G7",     [55, 59, 62, 65]),
    ("Busy",   "Am7",    [57, 60, 64, 67]),
    ("Heavy",  "Bdim",   [59, 62, 65, 68]),
    ("Crit",   "C High", [72, 76, 79, 83])
]

current_chord_name = "C Maj7"
current_chord_notes = CHORD_LEVELS[0][2]
current_mood = "Idle"

def get_chord_from_cpu(avg_cpu):
    idx = int((avg_cpu / 100.1) * len(CHORD_LEVELS))
    return CHORD_LEVELS[idx]

def get_weighted_note(chord_notes):
    if random.random() < 0.8: return random.choice(chord_notes)
    else: return random.choice(SCALE_NOTES)

# ==========================================
# 연주 함수 (6파트 - 볼륨 10% 하향 조정)
# ==========================================

# Core 0: Guitar Lead
def play_guitar_melody(cpu_val, duration):
    notes = current_chord_notes[:3]
    if cpu_val > 60: # High intensity
        note = random.choice(notes) + 12
        s.fork(lambda: guitar_lead.play_note(note, 0.54, duration)) # 0.6 -> 0.54
        return "Solo!"
    else: # Low intensity
        note = random.choice(notes)
        s.fork(lambda: guitar_lead.play_note(note, 0.45, duration)) # 0.5 -> 0.45
        return "Lick"

# Core 2: Guitar Chord (Strumming)
def play_guitar_strum(cpu_val, duration):
    # 다운 스트로크 느낌을 위해 약간의 시간차(arpeggiate) 없이 그냥 펑크 스타일로 팍!
    # 화음 구성: 루트 제외 상위 3음 (깔끔하게)
    notes = current_chord_notes[1:] 
    # 0.4 -> 0.36, divisor 300 -> 330
    vol = 0.36 + (cpu_val / 330)
    s.fork(lambda: guitar_chord.play_chord(notes, vol, duration * 2)) # 좀 더 길게 울림
    return f"Strum {current_chord_name}"

# Core 4: Keys Lead (Clavinet Funk)
def play_keys_funk(cpu_val, duration):
    base_note = get_weighted_note(current_chord_notes)
    if random.random() < 0.5: base_note += 12
    
    vol = 0.45 # 0.5 -> 0.45
    # 통통 튀는 짧은 음
    s.fork(lambda: keys_lead.play_note(base_note, vol, 0.15))
    return "Funk!"

# Core 6: Keys Chord (EP Comping)
def play_keys_comp(cpu_val, duration):
    notes = current_chord_notes
    # 0.4 -> 0.36, divisor 400 -> 440
    vol = 0.36 + (cpu_val / 440)
    # 부드럽게 깔아주는 코드
    s.fork(lambda: keys_chord.play_chord(notes, vol, duration * 4)) # 1초(4틱) 지속
    return "Pad"

# Core 8: Drums
def play_drums_groove(cpu_val, duration):
    parts = [42] # HH Closed
    if cpu_val > 20: parts.append(36) # Kick
    if cpu_val > 40: parts.append(38) # Snare
    
    for p in parts:
        s.fork(lambda: drum_kit.play_note(p, 0.7, duration))
    return "Beat"

# Core 10: Bass
def play_bass_foundation(cpu_val, duration):
    root = current_chord_notes[0] - 12
    if cpu_val > 50: note = root + 7
    else: note = root
    
    s.fork(lambda: bass_guitar.play_note(note, 1.0, duration))
    return f"Root {note}"

def apply_reverb(ram_percent):
    reverb_val = 10 + int(ram_percent * 1.1)
    if reverb_val > 127: reverb_val = 127
    
    for inst in [guitar_lead, guitar_chord, keys_lead, keys_chord, drum_kit, bass_guitar]:
        try:
            if hasattr(inst, 'play_cc'): inst.play_cc(91, reverb_val)
            elif hasattr(inst, 'send_cc'): inst.send_cc(91, reverb_val)
            elif hasattr(inst, 'control_change'): inst.control_change(91, reverb_val)
        except: pass
    return reverb_val

# ==========================================
# UI 및 상태 관리
# ==========================================
GRAPH_WIDTH = 20 # 6개라 폭 조금 줄임
vis_history = {i: deque([0]*GRAPH_WIDTH, maxlen=GRAPH_WIDTH) for i in range(6)}
system_state = {
    0: {"role": "Gtr Lead (Jazz)", "cpu": 0, "note": "-", "active": False, "enabled": True},
    1: {"role": "Gtr Chord (Cln)", "cpu": 0, "note": "-", "active": False, "enabled": True},
    2: {"role": "Key Lead (Clav)", "cpu": 0, "note": "-", "active": False, "enabled": True},
    3: {"role": "Key Chord (EP)",  "cpu": 0, "note": "-", "active": False, "enabled": True},
    4: {"role": "Drums (Groove)",  "cpu": 0, "note": "-", "active": False, "enabled": True},
    5: {"role": "Bass (Pick)",     "cpu": 0, "note": "-", "active": False, "enabled": True},
}

INSTRUMENTS = [guitar_lead, guitar_chord, keys_lead, keys_chord, drum_kit, bass_guitar]

def toggle_track(idx):
    system_state[idx]["enabled"] = not system_state[idx]["enabled"]
    if not system_state[idx]["enabled"]:
        try: INSTRUMENTS[idx].end_all_notes()
        except: pass

def get_sparkline(data_queue):
    levels = "  ▂▃▄▅▆▇█"
    return "".join([levels[int((v/100.1)*8)] for v in data_queue])

def generate_table(avg_cpu, ram_percent, reverb_val):
    color = "green" if avg_cpu < 40 else "yellow" if avg_cpu < 70 else "red"
    title = f"[bold {color}]CPU Symphony: {current_mood} ({current_chord_name}) | Load: {avg_cpu:.1f}%[/bold {color}]"
    subtitle = f"[dim]RAM Reverb: {ram_percent:.1f}% | 1-6 to Mute | 6-Core Ensemble[/dim]"
    
    table = Table(box=box.ROUNDED, title=title, caption=subtitle)
    table.add_column("Key", style="cyan", width=3, justify="center")
    table.add_column("Core", style="dim", width=6)
    table.add_column("Role", style="magenta", width=15)
    table.add_column("Load History", width=GRAPH_WIDTH)
    table.add_column("Val", justify="right", width=6)
    table.add_column("Status", style="green", width=14) 
    
    for i in range(6):
        state = system_state[i]
        if not state["enabled"]:
            style = "dim"; status_text = "[dim]MUTED[/dim]"; graph = "x" * GRAPH_WIDTH; val_text = "---"
        else:
            style = ""; status_text = state["note"] if not state["active"] else f"[bold white]{state['note']}[/bold white]"
            graph = f"[{color}]{get_sparkline(vis_history[i])}[/{color}]"
            val_text = f"{state['cpu']:.0f}%"
        if state["active"]: state["active"] = False
        table.add_row(f"[{i+1}]", f"#{TARGET_CORES[i]+1}", state["role"], graph, val_text, status_text, style=style)
    return Panel(table, expand=False)

def main():
    global current_chord_name, current_chord_notes, current_mood
    tick_count = 0
    logic_history = [[0.0]*3 for _ in range(6)]
    step_duration = 0.25 

    with Live(generate_table(0, 0, 0), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch()
                    if key == b'1': toggle_track(0)
                    elif key == b'2': toggle_track(1)
                    elif key == b'3': toggle_track(2)
                    elif key == b'4': toggle_track(3)
                    elif key == b'5': toggle_track(4)
                    elif key == b'6': toggle_track(5)
                
                time.sleep(step_duration)

                cpu_all = psutil.cpu_percent(interval=None, percpu=True)
                current_vals = [cpu_all[i] if i < len(cpu_all) else 0.0 for i in TARGET_CORES]
                avg_cpu = sum(current_vals) / len(current_vals)

                ram = psutil.virtual_memory().percent
                reverb_val = apply_reverb(ram)
                
                current_mood, current_chord_name, current_chord_notes = get_chord_from_cpu(avg_cpu)
                
                for i in range(6):
                    val = current_vals[i]
                    logic_history[i].pop(0); logic_history[i].append(val)
                    vis_history[i].append(val)
                    system_state[i]["cpu"] = val

                # --- 6 Core Logic ---
                
                # 1. Guitar Lead (Every 2 ticks, reactive)
                if system_state[0]["enabled"]:
                    if tick_count % 2 == 0:
                        system_state[0]["note"] = play_guitar_melody(current_vals[0], step_duration)
                        system_state[0]["active"] = True

                # 2. Guitar Chord (Every 4 ticks = 1 sec, on beat 1)
                if system_state[1]["enabled"]:
                    if tick_count % 4 == 0:
                        system_state[1]["note"] = play_guitar_strum(current_vals[1], step_duration)
                        system_state[1]["active"] = True

                # 3. Keys Lead (Random funk licks)
                if system_state[2]["enabled"]:
                    vals = logic_history[2]
                    is_peak = (vals[1] > vals[0] and vals[1] > vals[2])
                    if is_peak or random.random() < 0.2:
                        system_state[2]["note"] = play_keys_funk(vals[1], step_duration)
                        system_state[2]["active"] = True

                # 4. Keys Chord (Sustained Pad, every 4 ticks, on beat 1)
                if system_state[3]["enabled"]:
                    if tick_count % 4 == 0:
                        system_state[3]["note"] = play_keys_comp(current_vals[3], step_duration)
                        system_state[3]["active"] = True

                # 5. Drums (Every 2 ticks)
                if system_state[4]["enabled"]:
                    if tick_count % 2 == 0:
                        system_state[4]["note"] = play_drums_groove(current_vals[4], step_duration)
                        system_state[4]["active"] = True

                # 6. Bass (Every 4 ticks)
                if system_state[5]["enabled"]:
                    if tick_count % 4 == 0:
                        system_state[5]["note"] = play_bass_foundation(current_vals[5], step_duration)
                        system_state[5]["active"] = True

                tick_count += 1
                live.update(generate_table(avg_cpu, ram, reverb_val))

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
