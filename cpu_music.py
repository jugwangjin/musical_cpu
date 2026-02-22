import psutil
import time
import contextlib
import os
import logging
import random
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
console.print("[bold cyan]INITIATING THE POLYRHYTHMIC CLOCKWORK OS...[/bold cyan]")
console.print("[dim]Transforming CPU threads into interlocking minimalist gears.[/dim]")

s = Session(max_threads=2000)

# ==========================================
# 1. The Clockwork Instruments (Strictly Short Decay)
# ==========================================
INST_BASS = s.new_part("Electric Bass (finger)")
INST_CHORDS = s.new_part("Electric Piano 1")
INST_ARP3 = s.new_part("Marimba")
INST_ARP5 = s.new_part("Pizzicato Strings")
INST_COUNTER = s.new_part("Acoustic Guitar (nylon)")
INST_MELODY = s.new_part("Vibraphone")
INST_PERC = s.new_part("Woodblock")
INST_DRUM = s.new_part("Standard Drum Kit")

# ==========================================
# 2. Harmonic Stress Engine (Mood -> Scale)
# ==========================================
# C root = 48
ROOT = 48
SCALES = {
    "RELAXED (Major Pentatonic)": [0, 2, 4, 7, 9],       # 0-30%
    "FOCUSED (Dorian)": [0, 2, 3, 5, 7, 10],             # 30-60%
    "STRESSED (Harmonic Minor)": [0, 2, 3, 5, 7, 8, 11], # 60-85%
    "PANIC (Diminished)": [0, 1, 3, 4, 6, 7, 9, 10]      # 85-100%
}

def get_scale_for_cpu(global_cpu):
    if global_cpu < 30:
        return "RELAXED (Major Pentatonic)", SCALES["RELAXED (Major Pentatonic)"]
    elif global_cpu < 60:
        return "FOCUSED (Dorian)", SCALES["FOCUSED (Dorian)"]
    elif global_cpu < 85:
        return "STRESSED (Harmonic Minor)", SCALES["STRESSED (Harmonic Minor)"]
    else:
        return "PANIC (Diminished)", SCALES["PANIC (Diminished)"]

# ==========================================
# 3. Main Loop
# ==========================================
def main():
    tick = 0
    step_duration = 0.15 # ~100 BPM 16th notes (fast, clock-like)
    
    # Prime psutil
    psutil.cpu_percent()
    psutil.cpu_percent(percpu=True)
    
    gears = [
        {"name": "BASS (Root/5th)", "part": INST_BASS, "rhythm": 8, "offset": 0, "octave": -1, "base_prob": 90, "type": "bass"},
        {"name": "CHORDS (Syncop)", "part": INST_CHORDS, "rhythm": 8, "offset": 4, "octave": 0, "base_prob": 80, "type": "chord"},
        {"name": "ARP 3 (Marimba)", "part": INST_ARP3, "rhythm": 3, "offset": 0, "octave": 1, "base_prob": 60, "type": "arp"},
        {"name": "ARP 5 (Pizz.Str)", "part": INST_ARP5, "rhythm": 5, "offset": 0, "octave": 1, "base_prob": 50, "type": "arp"},
        {"name": "COUNTER (Guitar)", "part": INST_COUNTER, "rhythm": 6, "offset": 0, "octave": 1, "base_prob": 50, "type": "arp"},
        {"name": "MELODY (Vibes)", "part": INST_MELODY, "rhythm": 7, "offset": 0, "octave": 2, "base_prob": 40, "type": "melody"},
        {"name": "HI-HAT (Drums)", "part": INST_DRUM, "rhythm": 2, "offset": 0, "octave": 0, "base_prob": 80, "type": "hihat"},
        {"name": "WOODBLOCK", "part": INST_PERC, "rhythm": 4, "offset": 2, "octave": 0, "base_prob": 60, "type": "wood"},
    ]
    
    # Keep track of active notes for the UI
    gear_status = ["-" for _ in range(8)]
    
    def render_ui(global_cpu, mood_name, cores):
        table = Table(box=box.MINIMAL_DOUBLE_HEAD, title=f"[bold cyan]⚙️ THE POLYRHYTHMIC CLOCKWORK OS ⚙️[/bold cyan]\n[dim]Global Load: {global_cpu:.1f}% | Harmonic Mood: {mood_name}[/dim]")
        table.add_column("Gear (Instrument)", style="cyan", width=22)
        table.add_column("Core Mapping", justify="center", width=12)
        table.add_column("Core Load", justify="right", width=10)
        table.add_column("Rhythm", justify="center", width=10)
        table.add_column("Activity", justify="center", width=14)
        
        for i, g in enumerate(gears):
            core_idx = i % len(cores)
            c_load = cores[core_idx]
            
            # Color code activity
            act = gear_status[i]
            if act != "-":
                act_str = f"[bold green]{act}[/bold green]"
            else:
                act_str = "[dim]-[/dim]"
                
            # Rhythm fraction (e.g., 3/8, 1/3)
            phase = tick % g["rhythm"]
            r_str = f"{phase+1}/{g['rhythm']}"
            
            table.add_row(
                g["name"],
                f"Core {core_idx}",
                f"{c_load:.1f}%",
                r_str,
                act_str
            )
            
        return Panel(table, expand=False, border_style="cyan")

    with Live(render_ui(0.0, "INITIALIZING", [0.0]*8), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                # 1. Update CPU and determine Mood
                global_cpu = psutil.cpu_percent(interval=None)
                cores = psutil.cpu_percent(percpu=True, interval=None)
                if not cores:
                    cores = [global_cpu] # Fallback
                    
                mood_name, current_scale = get_scale_for_cpu(global_cpu)
                
                # 2. Process each gear in the clockwork
                for i, g in enumerate(gears):
                    gear_status[i] = "-" # Reset status
                    
                    # Check rhythm offset (phase)
                    if (tick - g["offset"]) % g["rhythm"] == 0:
                        
                        # Check probability (Base + Core Load)
                        core_idx = i % len(cores)
                        c_load = cores[core_idx]
                        prob = g["base_prob"] + (c_load * 0.5) # Max +50% at 100% load
                        
                        if random.random() * 100 < prob:
                            # TRIGGER NOTE!
                            vol = 0.4 + (c_load / 250.0) # 0.4 to 0.8 volume
                            dur = 0.1 # Very short staccato
                            
                            if g["type"] == "bass":
                                # Play root or fifth
                                note = ROOT + (g["octave"] * 12) + random.choice([0, 7])
                                s.fork(lambda pt=g["part"], n=note, v=vol, d=dur: pt.play_note(n, v, d))
                                gear_status[i] = "BONG"
                                
                            elif g["type"] == "chord":
                                # Play 2 random notes from scale
                                notes = [ROOT + (g["octave"] * 12) + interval for interval in random.sample(current_scale, 2)]
                                s.fork(lambda pt=g["part"], ns=notes, v=vol, d=dur: pt.play_chord(ns, v, d))
                                gear_status[i] = "CHORD"
                                
                            elif g["type"] == "arp" or g["type"] == "melody":
                                # Play 1 random note from scale
                                note = ROOT + (g["octave"] * 12) + random.choice(current_scale)
                                s.fork(lambda pt=g["part"], n=note, v=vol, d=dur: pt.play_note(n, v, d))
                                gear_status[i] = "DING"
                                
                            elif g["type"] == "hihat":
                                # 42 = Closed Hi-hat
                                s.fork(lambda pt=g["part"], v=vol, d=dur: pt.play_note(42, v*0.7, d))
                                gear_status[i] = "TSS"
                                
                                # Add kick/snare on 8-tick boundary if drums
                                if tick % 8 == 0:
                                    s.fork(lambda pt=g["part"], v=vol, d=dur: pt.play_note(36, v, d)) # Kick
                                    gear_status[i] = "KICK"
                                elif tick % 8 == 4:
                                    s.fork(lambda pt=g["part"], v=vol, d=dur: pt.play_note(38, v, d)) # Snare
                                    gear_status[i] = "SNARE"
                                    
                            elif g["type"] == "wood":
                                # 76 = Woodblock
                                s.fork(lambda pt=g["part"], v=vol, d=dur: pt.play_note(76, v, d))
                                gear_status[i] = "TOC"

                live.update(render_ui(global_cpu, mood_name, cores))
                tick += 1
                time.sleep(step_duration)

        except KeyboardInterrupt:
            pass
        except Exception as e:
            import traceback
            with open("crash_log.txt", "w") as f:
                traceback.print_exc(file=f)

if __name__ == "__main__":
    main()