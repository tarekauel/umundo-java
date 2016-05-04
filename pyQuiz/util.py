import time

def mtime():
    """Returns the current unixtime in milliseconds (as integer)"""
    return int(round(time.time() * 1000))
