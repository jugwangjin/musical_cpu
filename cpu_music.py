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

# ==========================================
# 0. System Preparations
# ==========================================
for logger_name in ["root", "clockblocks", "scamp"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    from scamp import Session

console = Console()
console.print("[bold green]INITIATING THE LO-FI OS... (Harmonically Perfect Edition)[/bold green]")
console.print("[dim]Removing all sustained/dissonant instruments. Building a dynamic groove band...[/dim]")

s = Session(max_threads=1000)

# ==========================================
# 1. The Short-Decay "Chill" Instruments
# ==========================================
# 절대 소리가 길게 끌리지 않는(짧게 끊어지는) 악기들만 엄선
KEYS = s.new_part("Electric Piano 1")      # 부드러운 EP
LEAD = s.new_part("Vibraphone")            # 영롱하고 짧은 비브라폰
BASS = s.new_part("Electric Bass (finger)")# 단단한 베이스
DRUM = s.new_part("Standard Drum Kit")     # 드럼

# 프로세스 생성/제거 효과음 (귀에 거슬리지 않는 타악기)
POP_SND = s.new_part("Woodblock")
BELL_SND = s.new_part("Glockenspiel")

# ==========================================
# 2. Harmonic Engine (App Theme Songs)
# ==========================================
# 듣기 좋은 메이저/마이너 다이아토닉 화음만 사용
DIATONIC_CHORDS = [
    [0, 4, 7],     # I (Major)
    [2, 5, 9],     # ii (Minor)
    [4, 7, 11],    # iii (Minor)
    [5, 9, 12],    # IV (Major)
    [7, 11, 14],   # V (Major)
    [9, 12, 16],   # vi (Minor)
]

NOTES_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

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

def generate_app_theme(title):
    # 창 제목을 해시하여 "이 앱만의 고유한 4코드 진행과 멜로디 패턴"을 생성합니다.
    h = int(hashlib.md5(title.encode('utf-8')).hexdigest(), 16)
    
    # 1. Key (조성)
    root_offset = h % 12
    root_name = NOTES_NAMES[root_offset]
    root_midi = root_offset + 48 # C3
    
    # 2. Chord Progression (4 마디 화음 진행)
    # 항상 듣기 좋은 팝/재즈 진행 템플릿 중 하나를 고릅니다.
    prog_templates = [
        [0, 5, 3, 4], # I - vi - IV - V (클래식 팝)
        [1, 4, 0, 5], # ii - V - I - vi (재즈 턴어라운드)
        [3, 4, 2, 5], # IV - V - iii - vi (아련한 진행)
        [5, 3, 0, 4], # vi - IV - I - V (현대 팝)
    ]
    prog_idx = (h // 12) % len(prog_templates)
    progression = prog_templates[prog_idx]
    
    # 3. 멜로디 패턴 (16비트 그리드 중 어디서 연주할 것인가?)
    # 예: 1001010010010010 (1=연주, 0=쉼)
    melody_rhythm = []
    temp_h = h // 144
    for _ in range(16):
        melody_rhythm.append(temp_h % 2 == 1)
        temp_h = temp_h >> 1
        
    # 최소한의 멜로디가 있도록 보정
    if sum(melody_rhythm) < 4:
        melody_rhythm[0] = melody_rhythm[4] = melody_rhythm[8] = melody_rhythm[12] = True

    return root_name, root_midi, progression, melody_rhythm

# ==========================================
# 3. Main Loop (Dynamic Orchestration)
# ==========================================
def main():
    last_title = ""
    root_name = "C"
    root_midi = 48
    progression = [0, 5, 3, 4]
    melody_rhythm = [True] + [False]*15
    
    last_pids = set(psutil.pids())
    
    tick = 0
    step_duration = 0.2 # 75 BPM 기준 16분 음표 (Lo-Fi Chillhop 속도)
    
    def render_ui(cpu, band_active, title, chord_num):
        table = Table(box=box.ROUNDED, title="[bold green]🎧 LO-FI OS : APP THEME SESSIONS 🎧[/bold green]")
        table.add_column("Module", style="cyan", width=14)
        table.add_column("Status / Output", style="white", width=40)
        table.add_column("Band Member", style="magenta", width=20)
        
        table.add_row("👁️ ACTIVE APP", f"[bold yellow]{title[:35]}[/bold yellow]", f"Key: {root_name} Major")
        
        # Band activity visualization
        drum_st = "[bold green]ON[/]" if band_active['drum'] else "[dim]off[/]"
        bass_st = "[bold green]ON[/]" if band_active['bass'] else "[dim]off[/]"
        keys_st = "[bold green]ON[/]" if band_active['keys'] else "[dim]off[/]"
        lead_st = "[bold green]ON[/]" if band_active['lead'] else "[dim]off[/]"
        
        table.add_row("⚡ CPU (Arranger)", f"Load: {cpu:.1f}% -> Invites members", f"Drum: {drum_st} | Bass: {bass_st}")
        table.add_row("🎵 HARMONY", f"Playing Chord: {chord_num+1} / 4", f"Keys: {keys_st} | Lead: {lead_st}")
        
        # Melody rhythm display
        rhythm_str = "".join(["♪" if m else "-" for m in melody_rhythm])
        table.add_row("🎹 THEME MELODY", f"[cyan]{rhythm_str[:8]} {rhythm_str[8:]}[/cyan]", "App Signature")
        
        return Panel(table, expand=False, border_style="green")

    with Live(render_ui(0, {'drum':True,'bass':True,'keys':True,'lead':True}, "-", 0), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                # 1. 창이 바뀌면 "그 앱의 테마곡"으로 부드럽게 전환
                current_title = get_active_window_title()
                if current_title != last_title:
                    last_title = current_title
                    root_name, root_midi, progression, melody_rhythm = generate_app_theme(current_title)
                    tick = 0 
                
                # 2. CPU를 '밴드 멤버 소환' 용도로 사용 (Dynamic Orchestration)
                # 불쾌한 음을 추가하는 대신, CPU가 낮으면 조용하게, 높으면 풍성하게 "편곡"을 바꿉니다.
                cpu = psutil.cpu_percent()
                
                band_active = {
                    'drum': True,                 # 드럼은 항상 연주 (기본 비트)
                    'bass': True,                 # 베이스 항상 연주 (뼈대)
                    'keys': cpu > 10.0,           # CPU 10% 이상일 때 화음(건반) 등장
                    'lead': cpu > 30.0            # CPU 30% 이상일 때 멜로디(비브라폰) 등장
                }
                
                # 3. 프로세스 팝/드롭 효과음 (아주 짧고 귀여운 소리)
                current_pids = set(psutil.pids())
                new_procs = current_pids - last_pids
                dead_procs = last_pids - current_pids
                last_pids = current_pids
                
                if len(new_procs) > 0:
                    s.fork(lambda: POP_SND.play_note(72, 0.4, 0.1)) # '뾱'
                if len(dead_procs) > 0:
                    s.fork(lambda: BELL_SND.play_note(84, 0.3, 0.1)) # '띵'
                
                time.sleep(step_duration)

                # ==========================================
                # 4. 음악 연주 (절대 오버랩되지 않는 완벽한 화성학)
                # ==========================================
                measure = (tick // 16) % 4 # 4마디 루프
                beat_16th = tick % 16      # 1마디 안의 16비트 위치
                
                # 현재 마디의 화음 (Diatonic)
                chord_idx = progression[measure]
                current_chord = [root_midi + interval for interval in DIATONIC_CHORDS[chord_idx]]
                
                # 🥁 DRUMS (Lo-Fi Chillhop Groove)
                if band_active['drum']:
                    # Kick on 0, 10
                    if beat_16th in [0, 10]: 
                        s.fork(lambda: DRUM_PART.play_note(36, 0.7, 0.1))
                    # Snare (Rimshot) on 4, 12
                    if beat_16th in [4, 12]: 
                        s.fork(lambda: DRUM_PART.play_note(37, 0.6, 0.1))
                    # Hi-hat (8th notes)
                    if beat_16th % 2 == 0:
                        s.fork(lambda: DRUM_PART.play_note(42, 0.3, 0.1))
                    # CPU가 50%를 넘으면 16비트 하이햇 추가
                    if cpu > 50.0 and beat_16th % 2 != 0:
                        s.fork(lambda: DRUM_PART.play_note(42, 0.2, 0.1))

                # 🎸 BASS (짧게 끊어치는 핑거 베이스)
                if band_active['bass']:
                    bass_note = current_chord[0] - 12
                    if beat_16th in [0, 8, 10]:
                        s.fork(lambda: BASS.play_note(bass_note, 0.7, 0.15))

                # 🎹 KEYS (코드 반주, 절대 길게 끌지 않음)
                if band_active['keys']:
                    if beat_16th in [0, 6]: # 정박과 당김음(Syncopation)
                        s.fork(lambda: KEYS.play_chord(current_chord, 0.4, 0.25))

                # 🎼 LEAD (해시 기반 고유 멜로디)
                if band_active['lead']:
                    if melody_rhythm[beat_16th]:
                        # 현재 화음 구성음 중에서 랜덤으로 연주 (절대 불협화음 안 남)
                        melody_note = random.choice(current_chord) + 12
                        s.fork(lambda: LEAD.play_note(melody_note, 0.5, 0.15))

                live.update(render_ui(cpu, band_active, current_title, measure))
                tick += 1

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
