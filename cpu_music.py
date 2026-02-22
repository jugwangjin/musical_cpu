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
console.print("[bold magenta]INITIATING THE SYNTHWAVE GRID SEQUENCER...[/bold magenta]")
console.print("[dim]Strict 4/4 time. No more chaos. Just pure, driven groove.[/dim]")

s = Session(max_threads=2000)

# ==========================================
# 1. Strict Instruments (Punchy, No Mud)
# ==========================================
DRUM_KICK = s.new_part("Standard Drum Kit")  # Kick & Snare
DRUM_HAT = s.new_part("Standard Drum Kit")   # Hats
BASS = s.new_part("Synth Bass 1")            # Driving 16th note bass
CHORDS = s.new_part("Pad 2 (warm)")          # Plucky warm synth (we'll play it staccato)
ARP = s.new_part("Lead 2 (sawtooth)")        # 8-bit style arpeggio
LEAD = s.new_part("Lead 1 (square)")         # Main melody

# ==========================================
# 2. Strict Harmonic Structure
# ==========================================
# A classic, incredibly satisfying progression: vi - IV - I - V (Am - F - C - G)
# We will lock to C Major / A Minor so it always sounds good.
PROGRESSION = [
    {"name": "Am", "root": 45, "notes": [45, 48, 52]}, # A2, C3, E3
    {"name": "F",  "root": 41, "notes": [41, 45, 48]}, # F2, A2, C3
    {"name": "C",  "root": 48, "notes": [48, 52, 55]}, # C3, E3, G3
    {"name": "G",  "root": 43, "notes": [43, 47, 50]}  # G2, B2, D3
]

# Scale for melody (A minor pentatonic / C major pentatonic = 100% safe notes)
SAFE_SCALE = [0, 2, 4, 7, 9, 12, 14, 16] 

# ==========================================
# 3. CPU-Driven Sequence Patterns (16 steps)
# ==========================================
# 1 = Play, 0 = Rest, X = Accent
# As CPU goes up (Levels 0, 1, 2), the pattern gets denser, but STAYS on grid.

PATTERNS = {
    "kick": [
        [1,0,0,0, 0,0,0,0, 1,0,0,0, 0,0,0,0], # Low CPU: Simple 4-on-the-floor (half time)
        [1,0,0,0, 0,0,0,0, 1,0,1,0, 0,0,0,0], # Med CPU: Add syncopation
        [1,0,0,1, 0,0,1,0, 1,0,0,0, 0,1,0,0]  # High CPU: Busy kick
    ],
    "snare": [
        [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0], # Always plays on 2 and 4 (beats 4 and 12 in 16ths)
        [0,0,0,0, 1,0,0,0, 0,0,0,0, 1,0,0,0],
        [0,0,0,0, 1,0,0,1, 0,0,0,0, 1,0,0,1]  # High CPU: Ghost notes
    ],
    "hat": [
        [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0], # Low: 8th notes
        [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1], # Med: 16th notes
        [2,1,2,1, 2,1,2,1, 2,1,2,1, 2,1,2,1]  # High: 16ths with accents (2=accent)
    ],
    "bass": [
        [1,0,0,0, 1,0,0,0, 1,0,0,0, 1,0,0,0], # Low: Quarter notes
        [1,1,0,1, 1,1,0,1, 1,1,0,1, 1,1,0,1], # Med: Gallop rhythm
        [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1]  # High: Rolling 16ths
    ],
    "chords": [
        [1,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0], # Low: Pad hold (one hit per bar)
        [0,0,1,0, 0,0,1,0, 0,0,1,0, 0,0,1,0], # Med: Off-beats (Reggae/Synthwave stab)
        [1,0,0,1, 0,0,1,0, 1,0,0,1, 0,0,1,0]  # High: Syncopated stabs
    ],
    "arp": [
        [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0], # Low: Off
        [1,0,1,0, 1,0,1,0, 1,0,1,0, 1,0,1,0], # Med: 8th note arp
        [1,1,1,1, 1,1,1,1, 1,1,1,1, 1,1,1,1]  # High: 16th note arp
    ]
}

def get_level(cpu_percent):
    if cpu_percent < 20: return 0
    if cpu_percent < 60: return 1
    return 2

# ==========================================
# 4. Main Engine
# ==========================================
def main():
    tick = 0
    step_duration = 0.125 # 120 BPM 16th notes
    
    psutil.cpu_percent()
    psutil.cpu_percent(percpu=True)
    
    def render_ui(cpu, cores, measure, beat_16, chord_name):
        table = Table(box=box.ROUNDED, title=f"[bold magenta]👾 SYNTHWAVE CPU SEQUENCER 👾[/bold magenta]")
        table.add_column("Track", style="cyan", width=12)
        table.add_column("Level (CPU)", justify="center", width=12)
        table.add_column("Sequence", justify="left", width=36)
        
        # Determine levels based on cores
        lvl_kick = get_level(cores[0] if len(cores)>0 else cpu)
        lvl_hat = get_level(cores[1] if len(cores)>1 else cpu)
        lvl_bass = get_level(cores[2] if len(cores)>2 else cpu)
        lvl_chord = get_level(cores[3] if len(cores)>3 else cpu)
        lvl_arp = get_level(cores[4] if len(cores)>4 else cpu)
        
        tracks = [
            ("Kick/Snare", lvl_kick, PATTERNS["kick"][lvl_kick], PATTERNS["snare"][lvl_kick]),
            ("Hi-Hat", lvl_hat, PATTERNS["hat"][lvl_hat], None),
            ("Bass", lvl_bass, PATTERNS["bass"][lvl_bass], None),
            ("Chords", lvl_chord, PATTERNS["chords"][lvl_chord], None),
            ("Arp", lvl_arp, PATTERNS["arp"][lvl_arp], None),
        ]
        
        for name, lvl, pat1, pat2 in tracks:
            # Build visual sequence string
            seq_str = ""
            for i in range(16):
                if i == beat_16:
                    seq_str += "[white on magenta]"
                elif i % 4 == 0:
                    seq_str += "[cyan]"
                else:
                    seq_str += "[dim]"
                
                char = "-"
                if pat1[i] > 0: char = "■" if pat1[i]==1 else "▲"
                if pat2 and pat2[i] > 0: char = "X" # Snare overwrites kick visual
                
                seq_str += char + "[/]"
                if i % 4 == 3: seq_str += " "
                
            table.add_row(name, f"Lvl {lvl}", seq_str)
            
        # Add status footer
        table.add_row("", "", "")
        table.add_row("[bold]GLOBAL[/bold]", f"{cpu:.1f}%", f"Measure {measure+1}/4 | Chord: [bold yellow]{chord_name}[/bold yellow]")
        
        return Panel(table, expand=False, border_style="magenta")

    with Live(render_ui(0, [0]*8, 0, 0, "Am"), refresh_per_second=10, screen=True) as live:
        try:
            while True:
                # Time tracking
                measure = (tick // 16) % 4
                beat_16 = tick % 16
                
                # Update CPU every 16th note (fast response)
                global_cpu = psutil.cpu_percent(interval=None)
                cores = psutil.cpu_percent(percpu=True, interval=None)
                if not cores: cores = [global_cpu] * 8
                
                # Current Harmony
                current_chord = PROGRESSION[measure]
                chord_root = current_chord["root"]
                chord_notes = current_chord["notes"]
                
                # Get activity levels from cores
                lvl_kick = get_level(cores[0 % len(cores)])
                lvl_snare = get_level(cores[0 % len(cores)]) # Lock snare level to kick
                lvl_hat = get_level(cores[1 % len(cores)])
                lvl_bass = get_level(cores[2 % len(cores)])
                lvl_chord = get_level(cores[3 % len(cores)])
                lvl_arp = get_level(cores[4 % len(cores)])
                lvl_lead = get_level(cores[5 % len(cores)])
                
                # ------------------------------------------------
                # PLAY INSTRUMENTS (Strict Grid, No Overlap)
                # ------------------------------------------------
                
                # KICK (36)
                if PATTERNS["kick"][lvl_kick][beat_16] == 1:
                    s.fork(lambda: DRUM_KICK.play_note(36, 0.8, 0.1))
                
                # SNARE (38)
                if PATTERNS["snare"][lvl_snare][beat_16] == 1:
                    s.fork(lambda: DRUM_KICK.play_note(38, 0.9, 0.1))
                    
                # HI-HAT (42)
                hat_val = PATTERNS["hat"][lvl_hat][beat_16]
                if hat_val > 0:
                    vol = 0.6 if hat_val == 2 else 0.3 # Accent vs normal
                    s.fork(lambda: DRUM_HAT.play_note(42, vol, 0.05))
                    
                # BASS
                if PATTERNS["bass"][lvl_bass][beat_16] == 1:
                    # Octave jumping on off-beats for that classic synthwave feel
                    octave = -12 if beat_16 % 2 == 0 else 0
                    s.fork(lambda: BASS.play_note(chord_root + octave, 0.7, 0.1))
                    
                # CHORDS
                if PATTERNS["chords"][lvl_chord][beat_16] == 1:
                    # Short plucky stabs
                    s.fork(lambda: CHORDS.play_chord(chord_notes, 0.5, 0.15))
                    
                # ARP
                if PATTERNS["arp"][lvl_arp][beat_16] == 1:
                    # Sweep up and down the chord notes
                    arp_note = chord_notes[beat_16 % len(chord_notes)] + 12 # Up 1 octave
                    s.fork(lambda: ARP.play_note(arp_note, 0.4, 0.1))
                    
                # LEAD MELODY (Generative, strictly quantized)
                if lvl_lead > 0:
                    # Play random notes from safe scale, but lock to the grid
                    # Level 1: quarter notes (beat_16 % 4 == 0)
                    # Level 2: 8th notes (beat_16 % 2 == 0)
                    rhythm_mod = 4 if lvl_lead == 1 else 2
                    if beat_16 % rhythm_mod == 0:
                        # 60% chance to play to leave space
                        if random.random() < 0.6:
                            # Start melody on C4 (60)
                            melody_note = 60 + random.choice(SAFE_SCALE)
                            s.fork(lambda: LEAD.play_note(melody_note, 0.6, 0.2))

                # Update UI
                live.update(render_ui(global_cpu, cores, measure, beat_16, current_chord["name"]))
                
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