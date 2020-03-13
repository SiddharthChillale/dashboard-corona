import schedule
import time
import os
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S


print("Initiated at = ",now.strftime("%d/%m/%Y %H:%M:%S"))
print("\n\tRunning script now at...\t", now.strftime("%d/%m/%Y %H:%M:%S"))
# print("Script run for ", num_of_runs, " times")
os.system("python corona_vis.py")
print("\n\tNext Script run in 5 minutes\n")


def job():

    now = datetime.now()
    print("\n\tRunning script now at...\t", now.strftime("%d/%m/%Y %H:%M:%S"))
    # print("Script run for ", num_of_runs, " times")
    os.system("python corona_vis.py")
    print("\n\tNext Script run in 5 minutes\n")
# schedule.every(1).minutes.do(job)
schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    # time.sleep(1)
