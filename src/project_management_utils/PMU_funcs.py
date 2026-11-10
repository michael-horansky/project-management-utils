# -----------------------------------------------------------------------------
# -------------- Project Management Utilities: helper functions ---------------
# -----------------------------------------------------------------------------

import time

# -------------------- General string formatting functions --------------------

def st(a, w):
    if len(str(a)) >= w:
        return(str(a)[:w]) # we trim
    else:
        diff = w - len(str(a))
        return(" " * int(diff // 2) + str(a) + " " * int(diff - diff // 2))


# --------------------- Time string formatting functions ----------------------

time_units = [
        {
            True : 'd',
            False : ' days',
            'dur' : 60 * 60 * 24
        },
        {
            True : 'h',
            False : ' hours',
            'dur' : 60 * 60
        },
        {
            True : 'm',
            False : ' min',
            'dur' : 60
        },
        {
            True : 's',
            False : ' sec',
            'dur' : 1
        }
    ]

def dtstr(seconds, max_depth = 2, concise = False):
    # delta t to string



    # Dynamically chooses the right format
    # max_depth is the number of different measurements (e.g. max_depth = 2: "2 days 5 hours")
    for i in range(len(time_units)):
        if seconds >= time_units[i]['dur']:
            if max_depth == 1:
                return(f"{int(round(seconds / time_units[i]['dur']))}{time_units[i][concise]}")
            remainder = seconds % time_units[i]['dur']
            elapsed_time_units = int((seconds - remainder) / time_units[i]['dur'])
            if concise:
                return(f"{elapsed_time_units}{time_units[i][concise]}{dtstr(remainder, max_depth - 1)}")
            else:
                return(f"{elapsed_time_units}{time_units[i][concise]} {dtstr(remainder, max_depth - 1)}")
    # Milliseconds
    if concise:
        return(f"{int(round(seconds / 0.001))}ms")
    else:
        return(f"{int(round(seconds / 0.001))} ms")

def tsrt(timestamp, time_format = "%H:%M:%S"):
    # t to string
    return( time.strftime(time_format, time.localtime( timestamp )) )

