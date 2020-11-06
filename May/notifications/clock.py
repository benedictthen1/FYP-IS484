from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
from telegram_morning_noti import send_morning_message

# def job_function():
#     print("Hello World")

sched = BlockingScheduler()

# Schedule send_message to be called every 10 seconds
sched.add_job(send_morning_message, 'interval', seconds=10)

# sched.add_job(send_message, 'cron', hour=1,minute=14,timezone=utc)

sched.start()