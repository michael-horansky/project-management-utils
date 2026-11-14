# -----------------------------------------------------------------------------
# -------------- Project Management Utilities: helper functions ---------------
# -----------------------------------------------------------------------------

import time
from numbers import Number

# ----------------------- Text formatting and alignment -----------------------

def min_with_none(a, b):
    if b is None:
        return a
    return min(a, b)

def less_than_with_none(a, b):
    # if a<b or b is None, return True
    if b is None:
        return True
    if a is None:
        return False
    return a < b

def more_than_with_none(a, b):
    # if a>b or b is None, return True
    if b is None:
        return True
    if a is None:
        return False
    return a > b

def auto_hyphenate(obj):
    if isinstance(obj, str):
        return True
    return False

def wrap_text(text, w, min_w = None, hyphenate = False, n = 6):
    # Returns a list of strings: the lines of the properly wrapped text.

    res = []
    if min_w is not None and w < min_w:
        # Cannot print anything
        return []

    while len(text) > w:
        considered = text[:w]
        rest = text[w:]

        # A natural break is already available.
        if considered[-1] == " " or rest[0] == " ":
            line = considered.rstrip()
            text = rest.lstrip()
        else:
            # Look for a space among the last n characters.
            search_start = max(0, w - n)
            break_at = considered.rfind(" ", search_start)

            if break_at != -1:
                line = considered[:break_at]
                text = considered[break_at + 1:] + rest
            else:
                # No suitable space: hyphenate.
                if hyphenate:
                    line = considered[:-1] + "-"
                    text = considered[-1] + rest
                else:
                    line = considered
                    text = rest

        res.append(line)

    if text:
        res.append(text)

    return res

def auto_halign(obj):
    if isinstance(obj, Number):
        return "c"
    return "l"

def auto_valign(obj):
    return "t"


def standard_align(obj, align):
    if align is None:
        return (auto_halign(obj), auto_valign(obj))
    if isinstance(align, str) and len(align) == 1:
        if align == "t":
            return (auto_halign(obj), "t")
        elif align == "b":
            return (auto_halign(obj), "b")
        elif align == "l":
            return ("l", auto_valign(obj))
        elif align == "r":
            return ("r", auto_valign(obj))
        elif align == "c":
            return ("c", "c")
        else:
            return (auto_halign(obj), auto_valign(obj))
    elif (isinstance(align, str) or isinstance(align, tuple) or isinstance(align, list)) and len(align) == 2:
        if align[0] in ["l", "c", "r"]:
            halign = align[0]
        else:
            halign = auto_halign(obj)
        if align[1] in ["t", "c", "b"]:
            valign = align[1]
        else:
            valign = auto_valign(obj)
        return (halign, valign)
    return (auto_halign(obj), auto_valign(obj))


def st(a, w, c = ' ', align = "c", plain_len = None):
    if plain_len is None:
        plain_len = len(str(a))
    if plain_len >= w:
        return str(a)[:w] # we trim
    else:
        diff = w - plain_len
        if align == "c":
            # center align
            return (c * int(diff // 2) + str(a) + c * int(diff - diff // 2))
        elif align == "l":
            # left align
            return str(a) + c * diff
        elif align == "r":
            # right align
            return c * diff + str(a)

def valign(a, h, c = "", align = "c"):
    # here a is a list of elements.
    # We will add elements to the list until its length equals w.
    # The elements are populated by c (the filler object)

    if len(a) > h:
        return a[:h] # we trim
    diff = h - len(a)
    if align == "c":
        # center align
        return ([c] * int(diff // 2) + a + [c] * int(diff - diff // 2))
    elif align == "t":
        # top align
        return a + [c] * diff
    elif align == "b":
        # bottom align
        return [c] * diff + a

def wrap_and_halign(obj, w, c = ' ', align = None, min_w = None, hyphenate = None):
    if hyphenate is None:
        hyphenate = auto_hyphenate(obj)
    std_align = standard_align(obj, align)
    lines = wrap_text(str(obj), w, min_w = min_w, hyphenate = hyphenate)
    for i in range(len(lines)):
        lines[i] = st(lines[i], w, c, std_align[0])
    return lines

def wrap_and_align(obj, w, h, c = ' ', align = None, min_w = None, hyphenate = None, n = 6):
    if hyphenate is None:
        hyphenate = auto_hyphenate(obj)
    std_align = standard_align(obj, align)
    lines = wrap_text(str(obj), w, min_w = min_w, hyphenate = hyphenate, n = n)
    lines = valign(lines, h, "", std_align[1])
    for i in range(len(lines)):
        lines[i] = st(lines[i], w, c, std_align[0])
    return lines


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

            trailing_delim = ''
            if (not concise) and num_val != 0 and max_depth > 1:
                trailing_delim = ' '

            if force_width is None:
                if max_depth == 1:
                    return leading_str
                else:
                    return leading_str + trailing_delim + dtstr(remainder, max_depth - 1, concise, None, False)
            if len(leading_str) > force_width:
                if leading:
                    # We crop aggressively
                    return leading_str[:force_width]
                else:
                    # We cap it here
                    return ' ' * force_width
            elif len(leading_str) == force_width:
                # With the delim, we could potentially enter negative force_width
                return leading_str
            elif max_depth == 1:
                # Final term, left-justified
                return leading_str.ljust(force_width)
            else:
                tail_rec = dtstr(remainder, max_depth - 1, concise, force_width - len(leading_str + trailing_delim), False)
                if tail_rec == "":
                    return leading_str.ljust(force_width)
                else:
                    return leading_str + trailing_delim + tail_rec
    # Milliseconds
    num_val = int(round(seconds / 0.001))
    if num_val == 0 and not leading:
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

