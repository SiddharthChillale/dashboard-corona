import schedule
import time
import threading
import os
from datetime import datetime

# datetime object containing current date and time
now = datetime.now()
# dd/mm/YY H:M:S


print("Initiated at = ",now.strftime("%d/%m/%Y %H:%M:%S"))
# print("\n\tRunning script now at...\t", now.strftime("%d/%m/%Y %H:%M:%S"))
# # print("Script run for ", num_of_runs, " times")
# os.system("python corona_vis.py")
# print("\n\tNext Script run in 5 minutes\n")

def job():

    now = datetime.now()
    print("\n\tRunning script now at...\t", now.strftime("%d/%m/%Y %H:%M:%S"))
    # print("Script run for ", num_of_runs, " times")
    os.system("python corona_vis.py")
    print("\n\tNext Script run in 5 minutes\n")
# schedule.every(1).minutes.do(job)

def job2():
    print("printing")

def threaded_job(job_func):
    job_thread=threading.Threa(target=job_func)
    job_thread.start()
    time.sleep(12)
    job_thread.stop()
    job_thread.join()

# schedule.every(20).seconds.do(job).run()
schedule.every(20).seconds.do(threaded_job, job2).run()


while True:
    schedule.run_pending()
    # time.sleep(1)
