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
console.print("[bold cyan]Loading The Ultimate CPU Symphony... (Allocating 19 Instruments)[/bold cyan]")
console.print("[dim]This may take a few seconds as FluidSynth loads soundfonts.[/dim]")

s = Session(max_threads=1000)

# ==========================================
# 1. 장르별 악기 설정 (Pre-load)
# ==========================================
GENRE_NAMES = ["🎸 Jazz Funk", "👾 Cyberpunk", "🎻 Orchestral"]
GENRE_PARTS = []

# 0: Jazz Funk (기존)
GENRE_PARTS.append([
    s.new_part("Electric Guitar (jazz)"),
    s.new_part("Electric Guitar (clean)"),
    s.new_part("Clavinet"),
    s.new_part("Electric Piano 1"),
    s.new_part("Standard Drum Kit"),
    s.new_part("Electric Bass (pick)")
])

# 1: Cyberpunk (Synthwave)
GENRE_PARTS.append([
    s.new_part("Lead 1 (square)"),
    s.new_part("Lead 2 (sawtooth)"),
    s.new_part("Synth Bass 1"),
    s.new_part("Pad 3 (polysynth)"),
    s.new_part("Electronic Drum"),
    s.new_part("Synth Bass 2")
])

# 2: Orchestral (Symphony)
GENRE_PARTS.append([
    s.new_part("Violin"),
    s.new_part("String Ensemble 1"),
    s.new_part("Flute"),
    s.new_part("Choir Aahs"),
    s.new_part("Timpani"),
    s.new_part("Contrabass")
])

# Network Data Stream (공통)
data_stream_part = s.new_part("Glockenspiel")

TARGET_CORES = [0, 2, 4, 6, 8, 10]

# ==========================================
# 2. 전역 상태
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
master_volume = 1.0
current_genre_idx = 0
overdrive_mode = False

def get_chord_from_cpu(avg_cpu):
    idx = int((avg_cpu / 100.1) * len(CHORD_LEVELS))
    return CHORD_LEVELS[idx]

def get_weighted_note(chord_notes):
    if random.random() < 0.8: return random.choice(chord_notes)
    else: return random.choice(SCALE_NOTES)

# ==========================================
# 3. 연주 함수 (장르 대응)
# ==========================================

def play_lead(cpu_val, duration, inst):
    notes = current_chord_notes[:3]
    if cpu_val > 60:
        note = random.choice(notes) + 12
        vol = 0.54 * master_volume * (1.2 if overdrive_mode else 1.0)
        s.fork(lambda: inst.play_note(note, vol, duration))
        return "Solo!"
    else:
        note = random.choice(notes)
        vol = 0.45 * master_volume
        s.fork(lambda: inst.play_note(note, vol, duration))
        return "Lick"

def play_rhythm(cpu_val, duration, inst):
    notes = current_chord_notes[1:] 
    base_vol = 0.36 + (cpu_val / 330)
    vol = base_vol * master_volume
    # 오케스트라는 더 길게, 펑크는 짧게
    dur_mult = 4 if current_genre_idx == 2 else 2
    s.fork(lambda: inst.play_chord(notes, vol, duration * dur_mult)) 
    return f"Chord {current_chord_name}"

def play_counter(cpu_val, duration, inst):
    base_note = get_weighted_note(current_chord_notes)
    if random.random() < 0.5: base_note += 12
    vol = 0.45 * master_volume
    s.fork(lambda: inst.play_note(base_note, vol, 0.15))
    return "Counter!"

def play_pad(cpu_val, duration, inst):
    notes = current_chord_notes
    base_vol = 0.36 + (cpu_val / 440)
    vol = base_vol * master_volume
    dur_mult = 8 if current_genre_idx == 2 else 4
    s.fork(lambda: inst.play_chord(notes, vol, duration * dur_mult))
    return "Pad"

def play_drums(cpu_val, duration, inst):
    vol = 0.7 * master_volume
    if current_genre_idx == 2: # 오케스트라(Timpani)는 화음 근음을 칩니다.
        root = current_chord_notes[0] - 24
        parts = [root]
        if cpu_val > 40: parts.append(root + 7)
        for p in parts: s.fork(lambda: inst.play_note(p, vol, duration * 2))
        return "Timpani"
    else: # 일반 드럼 매핑
        parts = [42]
        if cpu_val > 20: parts.append(36)
        if cpu_val > 40: parts.append(38)
        for p in parts: s.fork(lambda: inst.play_note(p, vol, duration))
        return "Beat"

def play_bass(cpu_val, duration, inst):
    root = current_chord_notes[0] - 12
    if cpu_val > 50: note = root + 7
    else: note = root
    vol = 1.0 * master_volume
    dur_mult = 2 if current_genre_idx == 2 else 1
    s.fork(lambda: inst.play_note(note, vol, duration * dur_mult))
    return f"Root {note}"

def play_data_stream(net_kbps, duration):
    if net_kbps < 5: return "-"
    # 네트워크 트래픽이 많으면 글록켄슈필로 빠른 아르페지오 데이터 스트림 연주
    notes = current_chord_notes + [current_chord_notes[-1]+12]
    vol = min(1.0, 0.2 + (net_kbps / 2000.0)) * master_volume
    
    def arp():
        for _ in range(4): # 0.25초 동안 4개의 64분 음표 연주
            data_stream_part.play_note(random.choice(notes) + 24, vol, duration / 4)
    s.fork(arp)
    return f"{net_kbps:.0f}KB/s"

def apply_reverb(ram_percent):
    reverb_val = 10 + int(ram_percent * 1.1)
    if reverb_val > 127: reverb_val = 127
    
    for genre in GENRE_PARTS:
        for inst in genre:
            try:
                if hasattr(inst, 'play_cc'): inst.play_cc(91, reverb_val)
                elif hasattr(inst, 'control_change'): inst.control_change(91, reverb_val)
            except: pass
    try:
        if hasattr(data_stream_part, 'play_cc'): data_stream_part.play_cc(91, reverb_val)
    except: pass
    return reverb_val

# ==========================================
# 4. UI 및 상태 관리
# ==========================================
GRAPH_WIDTH = 20
vis_history = {i: deque([0]*GRAPH_WIDTH, maxlen=GRAPH_WIDTH) for i in range(7)} # 7트랙 (Core6 + Net1)
system_state = {
    0: {"role": "Lead",   "val": 0, "note": "-", "active": False, "enabled": True},
    1: {"role": "Rhythm", "val": 0, "note": "-", "active": False, "enabled": True},
    2: {"role": "Counter","val": 0, "note": "-", "active": False, "enabled": True},
    3: {"role": "Pad",    "val": 0, "note": "-", "active": False, "enabled": True},
    4: {"role": "Drums",  "val": 0, "note": "-", "active": False, "enabled": True},
    5: {"role": "Bass",   "val": 0, "note": "-", "active": False, "enabled": True},
    6: {"role": "Net Data", "val": 0, "note": "-", "active": False, "enabled": True}, # Track 7
}

def toggle_track(idx):
    system_state[idx]["enabled"] = not system_state[idx]["enabled"]
    if not system_state[idx]["enabled"]:
        try:
            if idx == 6: data_stream_part.end_all_notes()
            else:
                for genre in GENRE_PARTS: genre[idx].end_all_notes()
        except: pass

def get_sparkline(data_queue, is_net=False):
    levels = "  ▂▃▄▅▆▇█"
    spark = ""
    for val in data_queue:
        if is_net:
            # Net val: 0 ~ 2000KB/s
            idx = min(8, int((val / 2000.0) * 8))
        else:
            idx = int((val / 100.1) * 8)
        spark += levels[idx]
    return spark

def generate_table(avg_cpu, ram_percent, reverb_val):
    theme_color = "red" if overdrive_mode else ("green" if avg_cpu < 40 else "yellow")
    title = f"[bold {theme_color}]CPU Symphony: {current_mood} ({current_chord_name}) | Load: {avg_cpu:.1f}%[/bold {theme_color}]"
    if overdrive_mode: title += " [blink bold red]🔥 OVERDRIVE 🔥[/blink bold red]"
    
    vol_bars = int(master_volume * 10)
    vol_display = "█" * vol_bars + "░" * (10 - vol_bars)
    
    subtitle = f"[bold cyan]Genre: {GENRE_NAMES[current_genre_idx]}[/bold cyan] | Vol: {vol_display} | Z:Funk X:Cyber C:Orch | 1-7: Mute"
    
    table = Table(box=box.ROUNDED, title=title, caption=subtitle)
    table.add_column("Key", style="cyan", width=3, justify="center")
    table.add_column("Source", style="dim", width=6)
    table.add_column("Role", style="magenta", width=12)
    table.add_column("Activity History", width=GRAPH_WIDTH)
    table.add_column("Val", justify="right", width=8)
    table.add_column("Status", style="green", width=14) 
    
    for i in range(7):
        state = system_state[i]
        is_net = (i == 6)
        
        if not state["enabled"]:
            style = "dim"; status_text = "[dim]MUTED[/dim]"; graph = "x" * GRAPH_WIDTH; val_text = "---"
        else:
            style = "bold red" if (overdrive_mode and not is_net) else ""
            status_text = state["note"] if not state["active"] else f"[bold white]{state['note']}[/bold white]"
            
            graph_color = "cyan" if is_net else theme_color
            graph = f"[{graph_color}]{get_sparkline(vis_history[i], is_net)}[/{graph_color}]"
            
            if is_net: val_text = f"{state['val']:.0f}K"
            else: val_text = f"{state['val']:.0f}%"
            
        if state["active"]: state["active"] = False
        
        src_label = "NET" if is_net else f"#{TARGET_CORES[i]+1}"
        table.add_row(f"[{i+1}]", src_label, state["role"], graph, val_text, status_text, style=style)
        
    return Panel(table, expand=False)

# ==========================================
# 5. 메인 루프
# ==========================================
def main():
    global current_chord_name, current_chord_notes, current_mood, master_volume, current_genre_idx, overdrive_mode
    tick_count = 0
    logic_history = [[0.0]*3 for _ in range(6)]
    step_duration = 0.25 
    
    net_last = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv

    with Live(generate_table(0, 0, 0), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                if msvcrt.kbhit():
                    key = msvcrt.getch().lower()
                    if key in [b'1', b'2', b'3', b'4', b'5', b'6', b'7']:
                        toggle_track(int(key.decode()) - 1)
                    elif key == b'q': master_volume = max(0.0, master_volume - 0.05)
                    elif key == b'w': master_volume = min(1.0, master_volume + 0.05)
                    elif key == b'z': current_genre_idx = 0 # Funk
                    elif key == b'x': current_genre_idx = 1 # Cyberpunk
                    elif key == b'c': current_genre_idx = 2 # Orchestral
                
                time.sleep(step_duration)

                # OS Metrics
                cpu_all = psutil.cpu_percent(interval=None, percpu=True)
                current_vals = [cpu_all[i] if i < len(cpu_all) else 0.0 for i in TARGET_CORES]
                avg_cpu = sum(current_vals) / len(current_vals)
                
                net_now = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
                net_diff_kb = (net_now - net_last) / 1024.0 # KB/s since 0.25s
                net_last = net_now

                ram = psutil.virtual_memory().percent
                reverb_val = apply_reverb(ram)
                
                current_mood, current_chord_name, current_chord_notes = get_chord_from_cpu(avg_cpu)
                overdrive_mode = (avg_cpu > 80)
                
                # Update UI queues
                for i in range(6):
                    val = current_vals[i]
                    logic_history[i].pop(0); logic_history[i].append(val)
                    vis_history[i].append(val)
                    system_state[i]["val"] = val
                vis_history[6].append(net_diff_kb)
                system_state[6]["val"] = net_diff_kb

                # Active Instruments for Current Genre
                insts = GENRE_PARTS[current_genre_idx]

                # --- 6 Core Logic + 1 Net Logic ---
                
                # 1. Lead (Every 2 ticks)
                if system_state[0]["enabled"]:
                    if tick_count % 2 == 0:
                        system_state[0]["note"] = play_lead(current_vals[0], step_duration, insts[0])
                        system_state[0]["active"] = True

                # 2. Rhythm Chord (Every 4 ticks)
                if system_state[1]["enabled"]:
                    if tick_count % 4 == 0:
                        system_state[1]["note"] = play_rhythm(current_vals[1], step_duration, insts[1])
                        system_state[1]["active"] = True

                # 3. Counter Melody (Random Peaks)
                if system_state[2]["enabled"]:
                    vals = logic_history[2]
                    is_peak = (vals[1] > vals[0] and vals[1] > vals[2])
                    if is_peak or random.random() < 0.2:
                        system_state[2]["note"] = play_counter(vals[1], step_duration, insts[2])
                        system_state[2]["active"] = True

                # 4. Pad (Every 4 ticks)
                if system_state[3]["enabled"]:
                    if tick_count % 4 == 0:
                        system_state[3]["note"] = play_pad(current_vals[3], step_duration, insts[3])
                        system_state[3]["active"] = True

                # 5. Drums (Every 2 ticks)
                if system_state[4]["enabled"]:
                    if tick_count % 2 == 0:
                        system_state[4]["note"] = play_drums(current_vals[4], step_duration, insts[4])
                        system_state[4]["active"] = True

                # 6. Bass (Every 4 ticks)
                if system_state[5]["enabled"]:
                    if tick_count % 4 == 0:
                        system_state[5]["note"] = play_bass(current_vals[5], step_duration, insts[5])
                        system_state[5]["active"] = True

                # 7. Network Data Stream (Every tick)
                if system_state[6]["enabled"]:
                    note_str = play_data_stream(net_diff_kb, step_duration)
                    if note_str != "-":
                        system_state[6]["note"] = note_str
                        system_state[6]["active"] = True

                tick_count += 1
                live.update(generate_table(avg_cpu, ram, reverb_val))

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
