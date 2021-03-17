import pytz

from datetime import datetime


def get_time_now(timezone='America/Santiago'):
    """
    Gets local datetime for a specified timezone,
    default argument value sets the timezone to the Chilean one
    """
    return datetime.now(pytz.timezone(timezone)).time()
