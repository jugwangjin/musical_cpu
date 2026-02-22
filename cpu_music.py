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
console.print("[bold red]AWAKENING THE SENTIENT OS...[/bold red]")
console.print("[dim]Scanning neural pathways (CPU), memories (RAM), and senses (I/O, Focus)...[/dim]")

s = Session(max_threads=1000)

# ==========================================
# 1. The Synaptic Instruments
# ==========================================
# Instead of genres, we have a pool of "Thoughts"
LEAD_POOL = [
    s.new_part("Marimba"),            # Logical, mathy
    s.new_part("Vibraphone"),         # Dreamy
    s.new_part("Electric Guitar (jazz)"), # Human
    s.new_part("Oboe"),               # Melancholic
    s.new_part("Lead 8 (bass+lead)"), # Aggressive
    s.new_part("Kalimba")             # Playful
]

BASS_POOL = [
    s.new_part("Acoustic Bass"),
    s.new_part("Fretless Bass"),
    s.new_part("Synth Bass 2")
]

PAD_PART = s.new_part("Pad 1 (new age)")
DRUM_PART = s.new_part("Standard Drum Kit")

# ==========================================
# 2. The Emotional Scales (Musical Theory)
# ==========================================
SCALES = {
    "Ionian (Happy)":      [0, 2, 4, 5, 7, 9, 11],
    "Dorian (Dreamy)":     [0, 2, 3, 5, 7, 9, 10],
    "Phrygian (Dark)":     [0, 1, 3, 5, 7, 8, 10],
    "Lydian (Mystical)":   [0, 2, 4, 6, 7, 9, 11],
    "Mixolydian (Blues)":  [0, 2, 4, 5, 7, 9, 10],
    "Aeolian (Sad)":       [0, 2, 3, 5, 7, 8, 10],
    "Locrian (Tense)":     [0, 1, 3, 5, 6, 8, 10],
    "Pentatonic (Zen)":    [0, 2, 4, 7, 9],
    "Whole Tone (Alien)":  [0, 2, 4, 6, 8, 10],
    "Diminished (Fear)":   [0, 2, 3, 5, 6, 8, 9, 11]
}
NOTES_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# ==========================================
# 3. The Fractal Chaos Engine (Logistic Map)
# ==========================================
# x_n+1 = r * x_n * (1 - x_n)
chaos_x = 0.5

def get_fractal_note(r_param, scale_notes):
    global chaos_x
    # R parameter defines chaos level (3.0 to 4.0)
    # 3.0 = Simple repeating loop
    # 3.5 = Complex but structured cycle
    # 3.9 = Pure unpredictable chaos
    chaos_x = r_param * chaos_x * (1.0 - chaos_x)
    if chaos_x < 0.0: chaos_x = 0.01
    if chaos_x >= 1.0: chaos_x = 0.99
    
    # Map chaos value (0.0~1.0) to an index in our current scale
    idx = int(chaos_x * len(scale_notes))
    return scale_notes[idx], chaos_x

# ==========================================
# 4. OS Context Reading (The "Eyes")
# ==========================================
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
    # Hash the window title to deterministically select the Key, Scale, and Instruments
    h = int(hashlib.md5(title.encode('utf-8')).hexdigest(), 16)
    
    root_offset = (h % 12)
    root_name = NOTES_NAMES[root_offset]
    root_midi = root_offset + 60 # C4 to B4
    
    scale_idx = (h // 12) % len(SCALES)
    scale_name = list(SCALES.keys())[scale_idx]
    intervals = list(SCALES.values())[scale_idx]
    
    # Generate 3 octaves of the scale
    full_scale = []
    for oct in [-1, 0, 1]:
        for interval in intervals:
            full_scale.append(root_midi + interval + (oct * 12))
            
    lead_idx = (h // 144) % len(LEAD_POOL)
    bass_idx = (h // 576) % len(BASS_POOL)
    
    return root_name, scale_name, full_scale, lead_idx, bass_idx

# ==========================================
# 5. The Nervous System (Main Loop)
# ==========================================
def main():
    global chaos_x
    
    last_title = ""
    root_name = "C"
    scale_name = "Ionian (Happy)"
    full_scale = []
    lead_idx, bass_idx = 0, 0
    
    net_last = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
    disk_last = psutil.disk_io_counters().read_bytes + psutil.disk_io_counters().write_bytes
    
    # UI History
    r_history = deque([3.0]*40, maxlen=40)
    x_history = deque([0.5]*40, maxlen=40)
    
    step_duration = 0.25 # 16th notes
    tick = 0
    
    def render_ui(cpu, ram, r_val, x_val, net_kbps, disk_kbps):
        levels = "  ▂▃▄▅▆▇█"
        r_spark = "".join([levels[int(((v - 3.0)/1.0) * 8)] for v in r_history])
        x_spark = "".join([levels[int(v * 8)] for v in x_history])
        
        table = Table(box=box.MINIMAL_DOUBLE_HEAD, title="[blink bold red]🧠 SENTIENT OS SONIFICATION ENGINE[/blink bold red]")
        table.add_column("Sensor", style="cyan", width=12)
        table.add_column("Data Telemetry", style="white", width=40)
        table.add_column("Musical Translation", style="magenta", width=25)
        
        table.add_row("👁️ FOCUS", f"[bold yellow]{last_title[:38]}[/bold yellow]", f"{root_name} {scale_name}")
        table.add_row("⚡ CPU (Chaos)", f"[{'red' if cpu>80 else 'green'}]{cpu:.1f}%[/] -> r={r_val:.3f} [{r_spark}]", f"Fractal x_n = {x_val:.3f}")
        table.add_row("🧠 RAM (Space)", f"{ram:.1f}%", f"Reverb CC91: {int(10 + ram)}")
        table.add_row("🌐 NET (Breath)", f"{net_kbps:.1f} KB/s", f"Pad Swell Vol: {min(1.0, 0.2 + net_kbps/1000):.2f}")
        table.add_row("💾 DISK (Pulse)", f"{disk_kbps:.1f} KB/s", f"Percussion Hits")
        
        return Panel(table, expand=False, border_style="red")

    with Live(render_ui(0,0,3.0,0.5,0,0), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                # 1. Read Window Context (Changes the Song's DNA)
                current_title = get_active_window_title()
                if current_title != last_title:
                    last_title = current_title
                    root_name, scale_name, full_scale, lead_idx, bass_idx = generate_context_signature(current_title)
                    # Reset chaos slightly to mark a new thought
                    chaos_x = 0.5 
                
                time.sleep(step_duration)
                
                # 2. Read Physical Sensors
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                
                net_now = psutil.net_io_counters().bytes_recv + psutil.net_io_counters().bytes_sent
                net_kbps = (net_now - net_last) / 1024.0
                net_last = net_now
                
                disk_now = psutil.disk_io_counters().read_bytes + psutil.disk_io_counters().write_bytes
                disk_kbps = (disk_now - disk_last) / 1024.0
                disk_last = disk_now
                
                # 3. Calculate Chaos (r_param ranges from 3.0 to 3.99 based on CPU)
                # Idle CPU -> 3.2 (Calm, repeating arpeggios)
                # Max CPU -> 3.99 (Wild, non-repeating fractal solos)
                r_param = 3.1 + (cpu / 100.0) * 0.89
                
                # 4. Generate Fractal Melody
                note, x_val = get_fractal_note(r_param, full_scale)
                
                r_history.append(r_param)
                x_history.append(x_val)
                
                # Apply Reverb based on RAM
                try:
                    for p in LEAD_POOL + BASS_POOL + [PAD_PART, DRUM_PART]:
                        if hasattr(p, 'play_cc'): p.play_cc(91, int(10 + ram))
                except: pass

                # 5. Play the Thought (The Music)
                
                # Lead (Fractal Melody)
                if cpu > 10: # Only think if doing something
                    vol = min(1.0, 0.4 + (cpu/200.0))
                    # Staccato short notes
                    s.fork(lambda: LEAD_POOL[lead_idx].play_note(note, vol, 0.12))
                
                # Bass (Anchor - plays the root of the fractal segment)
                if tick % 4 == 0:
                    bass_note = full_scale[0] - 12 # Root minus 1 octave
                    if x_val > 0.5: bass_note += 7 # Perfect 5th
                    s.fork(lambda: BASS_POOL[bass_idx].play_note(bass_note, 0.8, 0.4))
                
                # Pad (Breath - controlled by Network)
                if tick % 8 == 0 and net_kbps > 1.0:
                    pad_notes = [full_scale[0], full_scale[2], full_scale[4]] # Triad
                    pad_vol = min(0.8, 0.2 + (net_kbps / 2000.0))
                    s.fork(lambda: PAD_PART.play_chord(pad_notes, pad_vol, 1.8))
                
                # Drums (Pulse - controlled by Disk I/O)
                if disk_kbps > 50.0:
                    # Heavy disk activity = Kick + Crash
                    s.fork(lambda: DRUM_PART.play_note(36, 1.0, 0.1)) # Kick
                    if disk_kbps > 500.0:
                        s.fork(lambda: DRUM_PART.play_note(49, 0.8, 0.1)) # Crash
                elif tick % 2 == 0 and cpu > 30:
                    # Light ticking
                    s.fork(lambda: DRUM_PART.play_note(42, 0.5, 0.1)) # Closed HH

                tick += 1
                live.update(render_ui(cpu, ram, r_param, x_val, net_kbps, disk_kbps))

        except KeyboardInterrupt:
            pass

if __name__ == "__main__":
    main()
