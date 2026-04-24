import time

def main():
    i = 0
    while True:
        if i < 60:
            print(f"\rRunTime: {i} second(s)", end="", flush=True)
        else:
            print(f"\rRunTime: {i/60:.2f} minute(s)", end="", flush=True)
        time.sleep(1)
        i += 1