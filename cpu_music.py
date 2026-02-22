import psutil
import time
import contextlib
import os
import logging
import msvcrt
from collections import deque
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.console import Console
from rich import box

# ==========================================
# 0. 로그 및 경고 강력 차단
# ==========================================
for logger_name in ["root", "clockblocks", "scamp"]:
    logging.getLogger(logger_name).setLevel(logging.ERROR)

with contextlib.redirect_stdout(open(os.devnull, 'w')):
    from scamp import Session

# ==========================================
# 1. 설정 및 초기화
# ==========================================
console = Console()
console.print("[bold yellow]Initializing Audio Engine... (Main Branch with Vol/Mute)[/bold yellow]")

s = Session(max_threads=1000)

# 악기 생성
guitar_chord = s.new_part("Classical Guitar")
guitar_melody = s.new_part("Electric Guitar (Jazz)")
piano_chord = s.new_part("Piano")
piano_melody = s.new_part("Electric Piano")

INSTRUMENTS = [guitar_chord, guitar_melody, piano_chord, piano_melody]

# 사용할 CPU 코어 인덱스 (0부터 시작: 0=1번, 3=4번, 6=7번, 9=10번)
TARGET_CORES = [0, 3, 6, 9]

# ==========================================
# 2. 음악 데이터 정의
# ==========================================
MELODY_NOTES = [60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81, 83, 84]
CHORDS = [
    [48, 52, 55], [50, 53, 57], [52, 55, 59], [53, 57, 60],
    [55, 59, 62], [57, 60, 64], [59, 62, 65], [60, 64, 67]
]
CHORD_NAMES = ["C", "Dm", "Em", "F", "G", "Am", "Bdim", "C (High)"]

# ==========================================
# 3. 상태 관리
# ==========================================
GRAPH_WIDTH = 30
vis_history = {
    0: deque([0]*GRAPH_WIDTH, maxlen=GRAPH_WIDTH),
    1: deque([0]*GRAPH_WIDTH, maxlen=GRAPH_WIDTH),
    2: deque([0]*GRAPH_WIDTH, maxlen=GRAPH_WIDTH),
    3: deque([0]*GRAPH_WIDTH, maxlen=GRAPH_WIDTH),
}

# enabled 필드 추가
system_state = {
    0: {"role": "Guitar Chord", "cpu": 0, "note": "-", "active": False, "enabled": True},
    1: {"role": "Guitar Melody", "cpu": 0, "note": "-", "active": False, "enabled": True},
    2: {"role": "Piano Chord", "cpu": 0, "note": "-", "active": False, "enabled": True},
    3: {"role": "Piano Melody", "cpu": 0, "note": "-", "active": False, "enabled": True},
}

master_volume = 1.0 # 0.0 ~ 1.0
base_vol = 0.6

def map_value(value, steps):
    idx = int((value / 100.1) * steps)
    return idx

def toggle_track(idx):
    system_state[idx]["enabled"] = not system_state[idx]["enabled"]
    if not system_state[idx]["enabled"]:
        try: INSTRUMENTS[idx].end_all_notes()
        except: pass

def play_chord_async(inst, usage_val, core_idx):
    if not system_state[core_idx]["enabled"]:
        return

    idx = map_value(usage_val, 8)
    notes = CHORDS[idx]
    chord_name = CHORD_NAMES[idx]
    system_state[core_idx]["note"] = chord_name
    system_state[core_idx]["active"] = True
    
    vol = base_vol * master_volume
    s.fork(lambda: inst.play_chord(notes, vol, 0.9))

def play_melody_async(inst, usage_val, core_idx):
    if not system_state[core_idx]["enabled"]:
        return

    idx = map_value(usage_val, 15)
    note = MELODY_NOTES[idx]
    system_state[core_idx]["note"] = f"Note {note}"
    system_state[core_idx]["active"] = True
    
    vol = (base_vol + 0.1) * master_volume
    s.fork(lambda: inst.play_note(note, vol, 0.2))

# ==========================================
# 4. 그래프 그리기 함수 (Sparkline)
# ==========================================
def get_sparkline(data_queue):
    levels = "  ▂▃▄▅▆▇█"
    spark_str = ""
    for val in data_queue:
        idx = int((val / 100.1) * 8)
        spark_str += levels[idx]
    return spark_str

# ==========================================
# 5. UI 생성 함수
# ==========================================
def generate_table():
    # 볼륨 상태 바 생성
    vol_bars = int(master_volume * 10)
    vol_display = "█" * vol_bars + "░" * (10 - vol_bars)
    
    subtitle = f"[dim]Vol: {vol_display} ({int(master_volume*100)}%) | Q/W: Vol -/+ | 1-4: Mute[/dim]"
    
    table = Table(box=box.ROUNDED, title="[bold cyan]CPU Music Generator (Live Graph)[/bold cyan]", caption=subtitle)
    table.add_column("Core", style="dim", width=6)
    table.add_column("Role", style="magenta", width=15)
    table.add_column("CPU Usage History (30 ticks)", width=GRAPH_WIDTH+10)
    table.add_column("Value", justify="right", width=6)
    table.add_column("Note", style="green", width=12)
    table.add_column("Act", justify="center", width=3)
    table.add_column("Status", style="yellow", width=8)

    for i in range(4):
        state = system_state[i]
        cpu = state["cpu"]
        
        # 실제 코어 번호 (0->1, 3->4 ...)
        real_core_num = TARGET_CORES[i] + 1
        
        graph = get_sparkline(vis_history[i])
        color = "red" if cpu > 80 else "yellow" if cpu > 50 else "blue"
        
        status_icon = "●" if state["active"] else " "
        if state["active"]:
            state["active"] = False 
        
        mute_status = "ON" if state["enabled"] else "[dim]MUTED[/dim]"
        if not state["enabled"]:
             graph = "x" * len(graph)
             state["note"] = "-"

        table.add_row(
            f"Core {real_core_num}",
            state["role"],
            f"[{color}]{graph}[/{color}]",
            f"{cpu:.1f}%",
            state["note"],
            status_icon,
            mute_status
        )
    return Panel(table, expand=False)

# ==========================================
# 6. 메인 루프
# ==========================================
def main():
    global master_volume
    logic_history = [[0.0]*3 for _ in range(4)]
    tick_count = 0
    
    with Live(generate_table(), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                # 키보드 입력 처리
                if msvcrt.kbhit():
                    key = msvcrt.getch().lower()
                    if key == b'1': toggle_track(0)
                    elif key == b'2': toggle_track(1)
                    elif key == b'3': toggle_track(2)
                    elif key == b'4': toggle_track(3)
                    elif key == b'q': 
                        master_volume = max(0.0, master_volume - 0.05)
                    elif key == b'w': 
                        master_volume = min(1.0, master_volume + 0.05)

                time.sleep(0.25)
                
                # 전체 CPU 사용량 가져오기
                cpu_all = psutil.cpu_percent(interval=None, percpu=True)
                
                # 지정된 코어(0, 3, 6, 9)의 값만 추출
                # (시스템 코어 수가 10개 미만일 경우 예외 처리)
                current_vals = []
                for idx in TARGET_CORES:
                    if idx < len(cpu_all):
                        current_vals.append(cpu_all[idx])
                    else:
                        current_vals.append(0.0)
                
                for i in range(4):
                    val = current_vals[i]
                    logic_history[i].pop(0)
                    logic_history[i].append(val)
                    vis_history[i].append(val)
                    system_state[i]["cpu"] = val

                # Logic
                if tick_count % 4 == 0:
                    play_chord_async(guitar_chord, current_vals[0], 0)

                vals = logic_history[1]
                if (vals[1] > vals[0] and vals[1] > vals[2]) or \
                   (vals[1] < vals[0] and vals[1] < vals[2]):
                    play_melody_async(guitar_melody, vals[1], 1)
                else:
                    system_state[1]["note"] = "-"

                if tick_count % 4 == 0:
                    play_chord_async(piano_chord, current_vals[2], 2)

                vals = logic_history[3]
                if (vals[1] > vals[0] and vals[1] > vals[2]) or \
                   (vals[1] < vals[0] and vals[1] < vals[2]):
                    play_melody_async(piano_melody, vals[1], 3)
                else:
                    system_state[3]["note"] = "-"

                tick_count += 1
                live.update(generate_table())

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
