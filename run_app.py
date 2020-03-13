import schedule
import time
import os

def job():
    print("\tRunning script now...\n")
    # print("Script run for ", num_of_runs, " times")
    os.system("python run_app.py")
    print("\n\tNext Script run in 12 hours\n")
# schedule.every(1).minutes.do(job)
schedule.every(1).hours.do(job)

while True:
    schedule.run_pending()
    # time.sleep(1)
