import datetime

def verify_ddmmyyyy(date_text):
    '''Verifies if a date in the format DD/MM/YYYY is valid'''
    try:
        datetime.datetime.strptime(date_text, '%d/%m/%Y')
    except ValueError:
        raise ValueError(f"Incorrect data format, {date_text}. Should be DD/MM/YYYY")

def verify_date_is_in_future(date_text):
    '''Verifies if a date in the format DD/MM/YYYY is in the future'''
    date = datetime.datetime.strptime(date_text, '%d/%m/%Y')
    if date < datetime.datetime.now():
        print(f"Date {date_text} is in the past")

def convert_ddmmyyyy_to_mmddyyyy(date_text):
    '''Converts a date in the format DD/MM/YYYY to MM/DD/YYYY'''
    date = datetime.datetime.strptime(date_text, '%d/%m/%Y')
    return date.strftime('%m/%d/%Y')