import psutil
import os

print(f"Physical Cores: {psutil.cpu_count(logical=False)}")
print(f"Logical Processors: {psutil.cpu_count(logical=True)}")
print(f"CPU Usage per Processor (1s interval):")
usage = psutil.cpu_percent(interval=1, percpu=True)
for i, u in enumerate(usage):
    print(f"  Processor {i}: {u}%")
