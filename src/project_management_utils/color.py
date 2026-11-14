# -----------------------------------------------------------------------------
# -------------------------------- class color --------------------------------
# -----------------------------------------------------------------------------
# A small structure which contains the ANSI color codes for fancy printing.

# ANSI escape codes (SGR parameters)

class color:
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    DEFAULT = '\033[39m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NOTUNDERLINE = '\033[24m'
    FAINT = '\033[2m'
    LIGHT = '\033[22m' # removes BOLD or FAINT without resetting color

    END = '\033[0m'

    class bg:
        BLACK = '\033[40m'
        RED = '\033[41m'
        GREEN = '\033[42m'
        YELLOW = '\033[43m'
        BLUE = '\033[44m'
        MAGENTA = '\033[45m'
        CYAN = '\033[46m'
        WHITE = '\033[47m'

        BRIGHT_BLACK = '\033[100m'
        BRIGHT_RED = '\033[101m'
        BRIGHT_GREEN = '\033[102m'
        BRIGHT_YELLOW = '\033[103m'
        BRIGHT_BLUE = '\033[104m'
        BRIGHT_MAGENTA = '\033[105m'
        BRIGHT_CYAN = '\033[106m'
        BRIGHT_WHITE = '\033[107m'

        DEFAULT = '\033[49m'

    hr = {
        'black' : {
            'f' : '\033[30m',
            'b' : '\033[40m',
            'bf' : '\033[90m',
            'bb' : '\033[100m'
            },
        'red' : {
            'f' : '\033[31m',
            'b' : '\033[41m',
            'bf' : '\033[91m',
            'bb' : '\033[101m'
            },
        'green' : {
            'f' : '\033[32m',
            'b' : '\033[42m',
            'bf' : '\033[92m',
            'bb' : '\033[102m'
            },
        'yellow' : {
            'f' : '\033[33m',
            'b' : '\033[43m',
            'bf' : '\033[93m',
            'bb' : '\033[103m'
            },
        'blue' : {
            'f' : '\033[34m',
            'b' : '\033[44m',
            'bf' : '\033[94m',
            'bb' : '\033[104m'
            },
        'magenta' : {
            'f' : '\033[35m',
            'b' : '\033[45m',
            'bf' : '\033[95m',
            'bb' : '\033[105m'
            },
        'cyan' : {
            'f' : '\033[36m',
            'b' : '\033[46m',
            'bf' : '\033[96m',
            'bb' : '\033[106m'
            },
        'white' : {
            'f' : '\033[37m',
            'b' : '\033[47m',
            'bf' : '\033[97m',
            'bb' : '\033[107m'
            }

        }

    @staticmethod
    def bg_highlight(c, msg, bright = True):
        if c not in color.hr.keys():
            raise ValueError(f"Unknown color identifier '{c}'.")
        b_pre = 'b' if bright else ''
        return color.hr[c][b_pre + 'b'] + (color.BLACK if bright else color.BRIGHT_WHITE) + msg + color.DEFAULT + color.bg.DEFAULT

    @staticmethod
    def fg_highlight(c, msg, bright = True):
        if c not in color.hr.keys():
            raise ValueError(f"Unknown color identifier '{c}'.")
        b_pre = 'b' if bright else ''
        return color.hr[c][b_pre + 'f'] + msg + color.DEFAULT

    @staticmethod
    def underline(msg):
        return color.UNDERLINE + msg + color.NOTUNDERLINE
