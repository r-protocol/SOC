# logging_utils.py
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

def log_debug(message):
    """Verbose debug logging, enabled when config.VERBOSE is True."""
    try:
        from src.config import VERBOSE  # late import to avoid cycles
    except Exception:
        VERBOSE = False
    if VERBOSE:
        print(f"{BColors.OKBLUE}[DEBUG]{BColors.ENDC} {message}")
