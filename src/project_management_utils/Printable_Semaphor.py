# -----------------------------------------------------------------------------
# ------------------------- class Printable_Semaphor --------------------------
# -----------------------------------------------------------------------------
# Extends class Semaphor. Equipped with printing procedures helpful to Journal.

from . import PMU_funcs

from .color import color
from .Semaphor import Semaphor

import time
import math


# ------------------------- class Printable_Semaphor --------------------------

class Printable_Semaphor(Semaphor):

    spinning_pipes = ["|", "/", "-", "\\"]

    def __init__(self, time_format = "%H:%M:%S"):
        super().__init__() # Initialises abstract Semaphor
        self.label = {}
        self.c = {}
        self.width = {}
        self.process_pipe_i = {}
        self.time_format = time_format

    def create_event(self, label, tau_space, update_on_every_tick = False, c = None, width = 20):
        new_ID = super().create_event(tau_space, update_on_every_tick)
        if c is None or if c not in color.hr.keys():
            c = 'green' # default
        self.label[new_ID] = label
        self.c[new_ID] = c
        self.width[new_ID] = max(width, 20)
        self.process_pipe_i[new_ID] = 0

        return(new_ID)

    def get_exit_msg(self, process_label, process_duration):
        return(f"Process '{process_label}' finished after {PMU_funcs.dtstr(process_duration)}.")

    def finish_event(self, S_ID):
        process_label = self.label[S_ID]

        del self.label[S_ID]
        del self.c[S_ID]
        del self.width[S_ID]
        del self.process_pipe_i[S_ID]

        process_duration = super().finish_event(S_ID)
        return (process_duration, self.get_exit_msg(process_label, process_duration))

    # ---------------------------- Update methods -----------------------------

    def update(self, S_ID, tau):
        self.process_pipe_i[S_ID] = (self.process_pipe_i[S_ID] + 1) % len(Printable_Semaphor.spinning_pipes)
        return super().update(S_ID, tau)

    def update(self, S_ID, tau_progress):
        self.process_pipe_i[S_ID] = (self.process_pipe_i[S_ID] + 1) % len(Printable_Semaphor.spinning_pipes)
        return super().progress(S_ID, tau_progress)

    def overtime(self, S_ID, tau_overtime):
        self.process_pipe_i[S_ID] = (self.process_pipe_i[S_ID] + 1) % len(Printable_Semaphor.spinning_pipes)
        return super().overtime(S_ID, tau_overtime)


    # --------------------- String representation methods ---------------------

    def get_ETA_str(self, S_ID):
        if self.processes[S_ID].ETA is None:
            # No way to estimate the ETA, as we're still waiting for the first event
            return 'unknown'
        return PMU_funcs.dtstr(self.processes[S_ID].ETA, concise = True)

    def get_percentage_str(self, S_ID):
        if self.processes[S_ID].N_div <= 100:
            # Integer percentage
            return f"{int(self.processes[S_ID].cur_tau / self.processes[S_ID].tau_max * 100):d}%"
        return f"{self.processes[S_ID].cur_tau / self.processes[S_ID].tau_max:.1%}"


    def progress_bar(self, S_ID, fancy = True):
        # Prints a progress bar for a given semaphor ID
        # Format: label | percentage | ETA

        ETA_str = self.get_ETA_str(S_ID)
        percentage_str = self.get_percentage_str(S_ID)

        pipe_delim = Printable_Semaphor.spinning_pipes[self.process_pipe_i[S_ID]]

        time_info_msg = f" {pipe_delim} {percentage_str} {pipe_delim} {ETA_str}"

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


