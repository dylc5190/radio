import sched
import time
import datetime
import subprocess

# Initialize the scheduler
scheduler = sched.scheduler(time.time, time.sleep)



schedules = [
    {"day": "Monday", "time": "4:00 AM", "site": "wncw"}, # Mar. ~ Nov. 4:00 AM. Otherwise 5:00 AM
    {"day": "Friday", "time": "4:00 AM", "site": "wncw"},
    {"day": "Sunday", "time": "5:00 AM", "site": "wncw"},
    {"day": "Sunday", "time": "7:00 AM", "site": "wncw"},
    {"day": "Sunday", "time": "8:00 AM", "site": "ksmu"}, # Mar. ~ Nov. 8:00 AM. Otherwise 9:00 AM
]


def calculate_next_target_day(day, time_str):
    now = datetime.datetime.now()
    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    target_weekday = days.index(day)

    days_ahead = (target_weekday - now.weekday() + 7) % 7
    if (
        days_ahead == 0
        and now.time() > datetime.datetime.strptime(time_str, "%I:%M %p").time()
    ):
        days_ahead += 7

    next_target_day = now + datetime.timedelta(days=days_ahead)
    target_time = datetime.datetime.strptime(time_str, "%I:%M %p").time()
    next_target_day = next_target_day.replace(
        hour=target_time.hour, minute=target_time.minute, second=0, microsecond=0
    )

    return next_target_day


def run_recorder(site):
    subprocess.Popen(["python", "radio.py", site], close_fds=True)


def next_schedule(next_target_day, site):
    next_target_day_timestamp = next_target_day.timestamp()
    scheduler.enterabs(next_target_day_timestamp, 1, run_recorder, (site,))
    print(f"Scheduled to record {site} at {next_target_day}")
    scheduler.run()


def schedule_key(schedule):
    next_target_day = calculate_next_target_day(schedule["day"], schedule["time"])
    now = datetime.datetime.now()
    return (next_target_day - now).total_seconds()


while True:
    # Sort schedules by how close each schedule is to the current time
    for schedule in schedules:
        next_target_day = calculate_next_target_day(schedule["day"], schedule["time"])
        schedule["date"] = next_target_day

    schedules.sort(key=lambda x: x["date"])

    for schedule in schedules:
        next_schedule(schedule["date"], schedule["site"])
