import psutil
import time
import contextlib
import os
import logging
import random
import msvcrt
import ctypes
import hashlib
from collections import deque
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import box
from scamp import Session

# ==========================================
# 0. System Preparations
# ==========================================
for logger_name in ["root", "clockblocks", "scamp"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    from scamp import Session

console = Console()
console.print("[bold magenta]INITIATING THE MULTIVERSE OS...[/bold magenta]")
console.print("[dim]Preloading 4 distinct universes (Genres). This takes a moment...[/dim]")

s = Session(max_threads=1000)

# ==========================================
# 1. The Multiverse Ensembles (Extreme Differences)
# ==========================================
# 각 "유니버스(장르)"마다 완전히 다른 악기, BPM, 박자(Time Signature), 스케일 셋을 가집니다.

UNIVERSES = []

# 0: 🌌 CYBER-DOOM (다크하고 압도적인 전자/오케스트라 혼합)
UNIVERSES.append({
    "name": "Cyber-Doom",
    "lead": s.new_part("Distortion Guitar"),
    "chord": s.new_part("Church Organ"),  
    "bass": s.new_part("Synth Bass 1"),
    "drum": s.new_part("Taiko Drum"),     
    "scale": [0, 1, 3, 4, 6, 7, 9, 10],   # Octatonic (극도의 긴장감)
    "base_bpm": 140,
    "time_sig": 5                         # 5/4 박자 (기괴하고 불안정함)
})

# 1: 🎋 ZEN GARDEN (동양적이고 여유로운 명상)
UNIVERSES.append({
    "name": "Zen Garden",
    "lead": s.new_part("Koto"),
    "chord": s.new_part("Shakuhachi"),    
    "bass": s.new_part("Acoustic Bass"),
    "drum": s.new_part("Woodblock"),      
    "scale": [0, 2, 4, 7, 9],             # Pentatonic (평화로움)
    "base_bpm": 60,
    "time_sig": 3                         # 3/4 박자 (왈츠, 여유로움)
})

# 2: 👾 8-BIT ARCADE (고전 게임기 사운드)
UNIVERSES.append({
    "name": "8-Bit Arcade",
    "lead": s.new_part("Lead 1 (square)"),
    "chord": s.new_part("Lead 2 (sawtooth)"),
    "bass": s.new_part("Synth Bass 2"),
    "drum": s.new_part("Electronic Drum"),
    "scale": [0, 2, 4, 5, 7, 9, 11],      # Major (밝고 경쾌함)
    "base_bpm": 160,
    "time_sig": 4                         # 4/4 박자 (질주감)
})

# 3: 🍸 MIDNIGHT JAZZ (나른한 바이브)
UNIVERSES.append({
    "name": "Midnight Jazz",
    "lead": s.new_part("Vibraphone"),
    "chord": s.new_part("Electric Piano 1"),
    "bass": s.new_part("Fretless Bass"),
    "drum": s.new_part("Standard Drum Kit"),
    "scale": [0, 2, 3, 5, 7, 9, 10],      # Dorian (세련된 우울함)
    "base_bpm": 90,
    "time_sig": 4                         # 4/4 박자 (그루브)
})

# 공통 특수 악기
# 1. 프로세스 탄생/죽음 알리미 (Cellular Automata)
LIFE_PART = s.new_part("Tubular Bells") 
DEATH_PART = s.new_part("Timpani")

NOTES_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# ==========================================
# 2. Chaos Fractal Engine
# ==========================================
chaos_x = 0.5
def get_fractal_note(r_param, scale_notes):
    global chaos_x
    chaos_x = r_param * chaos_x * (1.0 - chaos_x)
    if chaos_x <= 0.0: chaos_x = 0.01
    if chaos_x >= 1.0: chaos_x = 0.99
    idx = int(chaos_x * len(scale_notes))
    return scale_notes[idx], chaos_x

# ==========================================
# 3. Context & Sensor Reading
# ==========================================
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def get_mouse_pan():
    # 마우스 X 좌표를 읽어서 좌/우 스테레오 패닝(Panning) 값으로 변환 (0~127)
    pt = POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    pan_val = int((pt.x / max(1, screen_width)) * 127)
    return max(0, min(127, pan_val))

def get_active_window_title():
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        ctypes.windll.user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value
        return title if title else "Idle Desktop"
    except:
        return "Unknown Context"

def generate_context_signature(title):
    h = int(hashlib.md5(title.encode('utf-8')).hexdigest(), 16)
    
    universe_idx = h % len(UNIVERSES)
    uni = UNIVERSES[universe_idx]
    
    root_offset = ((h // 10) % 12)
    root_name = NOTES_NAMES[root_offset]
    root_midi = root_offset + 48 # C3
    
    scale_notes = [root_midi + iv for iv in uni["scale"]]
    # 3옥타브 확장
    full_scale = scale_notes + [n + 12 for n in scale_notes] + [n + 24 for n in scale_notes]
    
    return universe_idx, root_name, full_scale

# ==========================================
# 4. Main Core
# ==========================================
def main():
    global chaos_x
    
    last_title = ""
    uni_idx = 0
    root_name = "C"
    full_scale = [60, 62, 64, 65, 67, 69, 71]
    
    last_pids = set(psutil.pids())
    birth_count = 0
    death_count = 0
    
    r_history = deque([3.0]*30, maxlen=30)
    
    tick = 0
    
    def render_ui(cpu, r_val, pan, birth, death, title):
        uni = UNIVERSES[uni_idx]
        levels = "  ▂▃▄▅▆▇█"
        r_spark = "".join([levels[min(8, int(((v - 3.0)/1.0) * 8))] for v in r_history])
        
        table = Table(box=box.HEAVY, title=f"[bold cyan]🌌 THE MULTIVERSE OS : {uni['name']}[/bold cyan]")
        table.add_column("Dimension", style="magenta", width=14)
        table.add_column("Telemetry", style="white", width=45)
        table.add_column("Musical Translation", style="green", width=20)
        
        table.add_row("👁️ FOCUS (Hash)", f"[bold yellow]{title[:40]}[/bold yellow]", f"Key: {root_name} | Sig: {uni['time_sig']}/4")
        table.add_row("⚡ CPU (Chaos)", f"Load: {cpu:.1f}% -> r={r_val:.3f} [{r_spark}]", f"BPM: {uni['base_bpm']}")
        table.add_row("🖱️ MOUSE (Space)", f"Pan X-Axis: {pan}/127", "Stereo Panning (CC10)")
        table.add_row("🦠 PROCESS (Life)", f"Births: {birth} | Deaths: {death}", "Chime / Thud")
        
        return Panel(table, expand=False, border_style="blue")

    with Live(render_ui(0,3.0,64,0,0,"-"), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                current_title = get_active_window_title()
                if current_title != last_title:
                    last_title = current_title
                    uni_idx, root_name, full_scale = generate_context_signature(current_title)
                    chaos_x = 0.5 
                    tick = 0 # 리듬 초기화
                
                uni = UNIVERSES[uni_idx]
                time_sig = uni["time_sig"]
                
                # CPU 기반 BPM 변동
                cpu = psutil.cpu_percent()
                bpm = uni["base_bpm"] + (cpu / 2.0) # CPU가 높으면 조금 더 빨라짐
                step_duration = 60.0 / bpm / 4.0    # 16th note duration
                
                time.sleep(max(0.05, step_duration)) # 극한의 빠른 속도 방지
                
                # 카오스 변수 연산
                r_param = 3.1 + (cpu / 100.0) * 0.89
                r_history.append(r_param)
                
                # 마우스 패닝 적용
                pan_val = get_mouse_pan()
                for inst in [uni["lead"], uni["chord"], uni["bass"], uni["drum"]]:
                    try:
                        if hasattr(inst, 'play_cc'): inst.play_cc(10, pan_val)
                    except: pass

                # ==========================================
                # THE NEW IDEAS: PROCESS SONIFICATION
                # ==========================================
                # 프로세스가 새로 켜지거나(Birth) 꺼지면(Death) 음악에 개입함
                current_pids = set(psutil.pids())
                new_procs = current_pids - last_pids
                dead_procs = last_pids - current_pids
                last_pids = current_pids
                
                if len(new_procs) > 0:
                    birth_count += len(new_procs)
                    s.fork(lambda: LIFE_PART.play_note(full_scale[-1] + 12, 1.0, 0.5)) # 밝은 고음 차임벨
                if len(dead_procs) > 0:
                    death_count += len(dead_procs)
                    s.fork(lambda: DEATH_PART.play_note(full_scale[0] - 12, 1.0, 0.2)) # 무거운 저음 쿵
                
                # ==========================================
                # DYNAMIC RHYTHM & HARMONY (Per Time Signature)
                # ==========================================
                beat_in_measure = tick % (time_sig * 4) # 16th notes per measure
                
                # 1. CHORD (Rhythm)
                if beat_in_measure == 0:
                    # 첫 박자에 화음 때리기 (잔향을 극도로 짧게 해서 오버랩 방지)
                    chord_notes = [full_scale[0], full_scale[2], full_scale[4]]
                    s.fork(lambda: uni["chord"].play_chord(chord_notes, 0.5, 0.15))
                elif beat_in_measure == (time_sig * 2) and time_sig % 2 == 0:
                    # 짝수 박자 스네어 위치에 백비트
                    chord_notes = [full_scale[1], full_scale[3], full_scale[5]]
                    s.fork(lambda: uni["chord"].play_chord(chord_notes, 0.4, 0.15))

                # 2. BASS
                if beat_in_measure % 8 == 0:
                    s.fork(lambda: uni["bass"].play_note(full_scale[0] - 12, 0.8, 0.2))
                elif beat_in_measure % 4 == 0 and time_sig == 5:
                    # 5/4 박자의 독특한 베이스 그루브
                    s.fork(lambda: uni["bass"].play_note(full_scale[2] - 12, 0.6, 0.15))
                    
                # 3. DRUMS
                if beat_in_measure == 0:
                    s.fork(lambda: uni["drum"].play_note(36, 0.8, 0.1)) # Kick
                if beat_in_measure == (time_sig * 2) and time_sig != 3:
                    s.fork(lambda: uni["drum"].play_note(38, 0.8, 0.1)) # Snare (3/4 박자는 생략)
                if beat_in_measure % 2 == 0:
                    s.fork(lambda: uni["drum"].play_note(42, 0.4, 0.1)) # Hihat

                # 4. LEAD (Fractal Chaos based on CPU)
                if cpu > 40 or (tick % 4 == 0):
                    note, _ = get_fractal_note(r_param, full_scale)
                    lead_vol = min(1.0, 0.3 + (cpu/200.0))
                    s.fork(lambda: uni["lead"].play_note(note, lead_vol, 0.1)) # 매우 짧게 끊음

                live.update(render_ui(cpu, r_param, pan_val, birth_count, death_count, current_title))
                tick += 1

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
