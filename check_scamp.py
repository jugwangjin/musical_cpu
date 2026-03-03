import scamp
try:
    s = scamp.Session()
    p = s.new_part('piano')
    print("Methods related to CC:")
    for m in dir(p):
        if 'cc' in m.lower() or 'control' in m.lower():
            print(f"- {m}")
    
    # Try send_cc
    if hasattr(p, 'send_cc'):
        print("send_cc exists!")
    elif hasattr(p, 'control_change'):
        print("control_change exists!")
    elif hasattr(p, 'cc'):
        print("cc exists!")
    elif hasattr(p, 'play_cc'):
        print("play_cc exists!")
    else:
        print("No obvious CC method found.")

except Exception as e:
    print(f"Error: {e}")
