import datetime

date_ranges = [
    (datetime.date(2023, 2, 1), datetime.date(2023, 2, 3)),
    (datetime.date(2023, 2, 5), datetime.date(2023, 2, 8)),
    (datetime.date(2023, 2, 10), datetime.date(2023, 2, 12)),
]

target_month = 2

target_month_dates = []

for start_date, end_date in date_ranges:
    date_range = end_date - start_date
    for i in range(date_range.days + 1):
        date_obj = start_date + datetime.timedelta(days=i)
        if date_obj.month == target_month:
            target_month_dates.append(date_obj)

for day in range(1, 29):
    if datetime.date(2023, target_month, day) not in target_month_dates:
        print(f"There is at least one free day in  month {target_month}")
        break
    else:
        print(f"There are no free days in month {target_month}")
