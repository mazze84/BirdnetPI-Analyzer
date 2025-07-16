from datetime import datetime

def format_date(date, format=None):
    formatted_date = date

    if format is None:
        return formatted_date.strftime("%d %B %Y")
    else:
        return formatted_date.strftime("%d %B %Y")
