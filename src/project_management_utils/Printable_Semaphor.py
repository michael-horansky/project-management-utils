# -----------------------------------------------------------------------------
# ------------------------- class Printable_Semaphor --------------------------
# -----------------------------------------------------------------------------
# Extends class Semaphor. Equipped with printing procedures helpful to Journal.

import .PMU_funcs

from .color import color
from .Semaphor import Semaphor

import time
import math


# ------------------------- class Printable_Semaphor --------------------------

class Printable_Semaphor(Semaphor):

    def __init__(self, time_format = "%H:%M:%S"):
        super().__init__() # Initialises abstract Semaphor
        self.c = {}
        self.width = {}
        self.time_format = time_format

    def create_event(self, label, tau_space, update_on_every_tick = False, c = None, width = 20):
        new_ID = super().create_event(tau_space, update_on_every_tick)
        if c is None or if c not in color.hr.keys():
            c = 'green' # default
        self.label[new_ID] = label
        self.c[new_ID] = c
        self.width[new_ID] = max(width, 20)

    # --------------------- String representation methods ---------------------



    def progress_bar(self, S_ID, fancy = True):
        # Prints a progress bar for a given semaphor ID
        # Format: label | percentage | ETA

        ETA_str = PMU_funcs.dtstr(self.processes[S_ID].ETA, concise = True)
        if self.processes[S_ID].N_div <= 100:
            # Integer percentage
            percentage_str = f"{int(self.processes[S_ID].cur_tau / self.processes[S_ID].tau_max * 100):d}%"
        else:
            percentage_str = f"{self.processes[S_ID].cur_tau / self.processes[S_ID].tau_max:.1%}"
        time_info_msg = f" | {percentage_str} | {ETA_str}"

        label_max_w = self.width[S_ID] - len(time_info_msg)
        if label_max_w < 0:
            # This should never happen. We trim aggressively
            msg = (self.label[S_ID] + time_info_msg)[:self.width[S_ID]]
        elif label_max_w < len(self.label[S_ID]):
            msg = self.label[S_ID][:label_max_w] + time_info_msg
        else:
            msg = PMU_funcs.st(self.label[S_ID] + time_info_msg, self.width[S_ID])

        if not fancy:
            plain_res = f"[{msg}]"
            return plain_res

        # We insert the colors.

        N_color = math.floor(self.width[S_ID] * self.processes[S_ID].cur_tau / self.processes[S_ID].tau_max)

        fancy_res = f"[{color.hr[self.c[S_ID]]['bb']}{color.BLACK}{msg[:N_color]}{color.hr[self.c[S_ID]]['bf']}{color.bg.DEFAULT}{msg[N_color:]}{color.DEFAULT}]"
        return fancy_res

    def progress_bars(self, fancy = True):
        # Creates a progress bar for each active semaphor event.
        if len(self.processes) == 0:
            return ""
        res = ""
        for S_ID in self.processes.keys():
            res += self.progress_bar(S_ID, fancy) + " "
        return res[:-1]


