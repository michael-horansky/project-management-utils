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
            'concise' : 'd',
            'verbose' : 'days',
            'singular' : 'day',
            'dur' : 60 * 60 * 24
        },
        {
            'concise' : 'h',
            'verbose' : 'hours',
            'singular' : 'hour',
            'dur' : 60 * 60
        },
        {
            'concise' : 'm',
            'verbose' : 'min',
            'dur' : 60
        },
        {
            'concise' : 's',
            'verbose' : 'sec',
            'dur' : 1
        }
    ]

def get_time_unit(i, concise, val):
    if i is None:
        # ms
        if concise:
            return 'ms'
        else:
            return ' ms'

    if concise:
        return time_units[i]['concise']
    else:
        if val == 1 and 'singular' in time_units[i].keys():
            return ' ' + time_units[i]['singular']
        elif 'verbose' in time_units[i].keys():
            return ' ' + time_units[i]['verbose']
        else:
            return ' ' + time_units[i]['concise']


def dtstr(seconds, max_depth = 2, concise = False, force_width = None, leading = True):
    # delta t to string

    # Dynamically chooses the right format
    # max_depth is the number of different measurements (e.g. max_depth = 2: "2 days 5 hours")
    for i in range(len(time_units)):
        if seconds >= time_units[i]['dur']:
            if max_depth == 1:
                num_val = int(round(seconds / time_units[i]['dur']))
            else:
                remainder = seconds % time_units[i]['dur']
                num_val = int((seconds - remainder) / time_units[i]['dur'])

            if num_val == 0:
                leading_str = ""
            else:
                leading_str = str(num_val) + get_time_unit(i, concise, num_val)

            if (not concise) and num_val != 0 and max_depth > 1:
                leading_str += ' ' # delimiter from next value

            if force_width is None:
                if max_depth == 1:
                    return leading_str
                else:
                    return leading_str + dtstr(remainder, max_depth - 1, concise, None, False)
            if len(leading_str) > force_width:
                if leading:
                    # We crop aggressively
                    return leading_str[:force_width]
                else:
                    # We cap it here
                    return ' ' * force_width
            elif max_depth == 1:
                # Final term, left-justified
                return leading_str.ljust(force_width)
            else:
                return leading_str + dtstr(remainder, max_depth - 1, concise, force_width - len(leading_str), False)
    # Milliseconds
    num_val = int(round(seconds / 0.001))
    if num_val == 0:
        leading_str = ""
    else:
        leading_str = str(num_val) + get_time_unit(None, concise, num_val)
    if force_width is None:
        return leading_str
    if len(leading_str) > force_width:
        if leading:
            # We crop aggressively
            return leading_str[:force_width]
        else:
            # We cap it here
            return ' ' * force_width
    return leading_str.ljust(force_width)

def tsrt(timestamp, time_format = "%H:%M:%S"):
    # t to string
    return( time.strftime(time_format, time.localtime( timestamp )) )

