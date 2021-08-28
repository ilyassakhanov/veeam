import psutil
import subprocess


def get_cpu_precentage():
    return psutil.cpu_percent()

def get_memory(pid):
    process = psutil.Process(pid)
    info = process.memory_info()
    return info[0], info[1]


def get_handles(pid):
    process = psutil.Process(pid)
    handles = psutil.net_connections()
    return handles[0][0]


def start_process(path):
    proc = subprocess.Popen(path, shell=True)
    pid = proc.pid
    return pid


def main(pid):
    memory = get_memory(pid)
    handles = get_handles(pid)
    cpu_usage = get_cpu_precentage()
    # cpu-usage, resident-set-size, virtial-memory-size
    result = [cpu_usage,  memory[0], memory[1], handles]
    return result

