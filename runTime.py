import time

def main():
    i = 0
    while True:
        if i < 60:
            print(f"\rRunTime: {i} second(s)", end="", flush=True)
        else:
            print(f"\rRunTime: {int(i/60)}:{i-60*int(i/60)} minute(s)", end="", flush=True)
        time.sleep(1)
        i += 1