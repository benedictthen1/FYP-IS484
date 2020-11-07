from pytz import utc
from apscheduler.schedulers.blocking import BlockingScheduler
from send_telegram_whatsapp import send_to_telegram_whatsapp

sched = BlockingScheduler()

# Schedule send_message to be called every 5 seconds
sched.add_job(send_to_telegram_whatsapp, 'interval', seconds=5)

# sched.add_job(send_message, 'cron', hour=1,minute=14,timezone=utc)

sched.start()