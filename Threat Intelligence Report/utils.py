# utils.py
import datetime

# --- CONSOLE LOGGING SETUP ---
class BColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def log_info(message):
    print(f"{BColors.OKCYAN}[INFO]{BColors.ENDC} {message}")

def log_success(message):
    print(f"{BColors.OKGREEN}[SUCCESS]{BColors.ENDC} {message}")

def log_warn(message):
    print(f"{BColors.WARNING}[WARN]{BColors.ENDC} {message}")
    
def log_error(message):
    print(f"{BColors.FAIL}[ERROR]{BColors.ENDC} {message}")

def log_step(step_number, message):
    print(f"\n{BColors.BOLD}{BColors.HEADER}--- PHASE {step_number}: {message} ---{BColors.ENDC}")

def get_last_full_week_dates():
    """Calculates the start and end dates for the previous full calendar week (Monday to Sunday)."""
    today = datetime.date.today()
    # today.weekday() is 0 for Monday, 6 for Sunday.
    # To get to the *previous* Sunday, we subtract (today.weekday() + 1) days.
    end_date = today - datetime.timedelta(days=(today.weekday() + 1))
    # The start date is 6 days before the end date.
    start_date = end_date - datetime.timedelta(days=6)
    return start_date, end_date