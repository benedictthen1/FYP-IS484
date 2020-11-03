from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
from whatsapp_twilio_testing import send_message

# def job_function():
#     print("Hello World")

sched = BlockingScheduler()

# Schedule send_message to be called every 10 seconds
# sched.add_job(send_message, 'interval', seconds=1)

sched.add_job(send_message, 'cron', hour=1,minute=14,timezone=utc)

sched.start()