import time

i = 0

def calculate_update_times(successes):
    if successes > 0:
        return f"{i/successes:.2f}"

def main():
    global i
    while True:
        if i < 60:
            print(f"\rRunTime: {i} second(s)", end="", flush=True)
        else:
            print(f"\rRunTime: {int(i/60)}:{i-60*int(i/60)} minute(s)", end="", flush=True)
        time.sleep(1)
        i += 1