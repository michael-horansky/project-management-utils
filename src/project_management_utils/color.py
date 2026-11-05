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

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NOTUNDERLINE = '\033[24m'
    LIGHT = '\033[22m' # removes BOLD without resetting color
    DISABLE = '\033[02m'
    END = '\033[0m'

    class bg:
        BLACK = '\033[40m'
        RED = '\033[41m'
        GREEN = '\033[42m'
        ORANGE = '\033[43m'
        BLUE = '\033[44m'
        PURPLE = '\033[45m'
        CYAN = '\033[46m'
        GREY = '\033[47m'
        DEFAULT = '\033[49m'
