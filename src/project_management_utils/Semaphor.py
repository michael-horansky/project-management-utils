# -----------------------------------------------------------------------------
# ------------------------------ class Semaphor -------------------------------
# -----------------------------------------------------------------------------
# Manages asynchronous progress bars and calculates estimated times of finish.
# Auxiliary class for Journal; does not manage printing at all.

from numbers import Number
import time
import numpy as np
import math

class ProcessTracker():
    # Tracks a single process
    def __init__(self, tau_space, update_on_every_tick):
        # "Tau" is simulation time, "t" is real time

        # Real time management
        self.t_start = time.time() # current timestamp
        self.ETA = None # Only calculable when cur_tau > 0. This is the time interval expected to pass before finish, in seconds.

        # Sim time management
        self.tau_max, self.N_div = self.sanitise_tau_space(tau_space)

        self.cur_tau = 0.0 # We mark the beginning
        self.cur_tau_index = 0

        # If update_on_every_tick, an update signal is sent out every time tau or tau_max update.
        # Otherwise, an update signal is only sent out if cur_tau_index changes
        self.update_on_every_tick = update_on_every_tick

    def sanitise_tau_space(self, tau_space, default_N_div = 1000):
        # Normalises tau space into tau_max, N_div.
        # Allowed values:
        #   -tuple of length 2. First element is interpreted as max tau value, second element as number of divisions.
        #   -number. Interpreted as max tau value. Number of divisions defaults to the provided default value or 1000.

        if isinstance(tau_space, tuple):
            if len(tau_space) == 2:
                return(tau_space)
            else:
                raise ValueError("Tuple tau_space must have a length of 2.")

        if isinstance(tau_space, Number):
            return(tau_space, default_N_div)

        raise TypeError(f"Unexpected tau_space type: {type(tau_space)}")

    def get_index(self, x, max_x):
        if self.update_on_every_tick:
            # No need to track index, we remain at default value
            return(0)

        if x <= 0:
            return(0)
        if x >= max_x:
            return(self.N_div) # the final index, equivalent to "finished"
        return(math.floor(x * self.N_div / max_x))

    def update(self, tau):
        # Updates current tau value. Returns True if update needed, False otherwise.
        new_index = self.get_index(tau, self.tau_max)
        need_update = new_index != self.cur_tau_index

        self.cur_tau = tau
        self.cur_tau_index = new_index

        if need_update or self.update_on_every_tick:
            self.update_ETA()

        return(need_update or self.update_on_every_tick)

    def progress(self, tau_progress = 1):
        # Increases current tau value. Returns True if update needed, False otherwise.
        new_index = self.get_index(self.cur_tau + tau_progress, self.tau_max)
        need_update = new_index != self.cur_tau_index

        self.cur_tau += tau_progress
        self.cur_tau_index = new_index

        if need_update or self.update_on_every_tick:
            self.update_ETA()

        return(need_update or self.update_on_every_tick)

    def overtime(self, tau_overtime = 1):
        # Unpredicted workload was done. Increases both tau and max_tau by tau_overtime. Returns True if update needed, False otherwise.
        new_index = self.get_index(self.cur_tau + tau_overtime, self.tau_max + tau_overtime)
        need_update = new_index != self.cur_tau_index

        self.cur_tau += tau_overtime
        self.tau_max += tau_overtime
        self.cur_tau_index = new_index

        if need_update or self.update_on_every_tick:
            self.update_ETA()

        return(need_update or self.update_on_every_tick)

    def update_ETA(self):
        if self.cur_tau == 0.0:
            self.ETA = None
        elif self.cur_tau >= self.tau_max:
            self.ETA = 0
        else:
            self.ETA = (time.time() - self.t_start) * (self.tau_max / self.cur_tau - 1)



class Semaphor():

    def __init__(self):
        self.N_events = 0

        self.processes = {}

    # --------------------------- internal methods ----------------------------



    def create_event(self, tau_space, update_on_every_tick = False):
        # newline should be set to True for nested events, False for the innermost events or non-nested events

        # New ID
        new_ID = f"S_EVENT_{self.N_events}"
        self.N_events += 1

        self.processes[new_ID] = ProcessTracker(tau_space, update_on_every_tick)
        return(new_ID)

    def finish_event(self, event_ID):
        # Returns the duration in ms
        if event_ID not in self.processes.keys():
            raise Exception(f"  ERROR: Semaphor '{event_ID}' does not exist.")

        process_duration = time.time() - self.processes[event_ID].t_start

        del self.processes[event_ID]

        return(process_duration)

    def update(self, event_ID, tau):
        if event_ID not in self.processes.keys():
            raise Exception(f"  ERROR: Semaphor '{event_ID}' does not exist.")
        return self.processes[event_ID].update(tau)

    def progress(self, event_ID, tau_progress = 1):
        if event_ID not in self.processes.keys():
            raise Exception(f"  ERROR: Semaphor '{event_ID}' does not exist.")
        return self.processes[event_ID].progress(tau_progress)

    def overtime(self, event_ID, tau_overtime = 1):
        if event_ID not in self.processes.keys():
            raise Exception(f"  ERROR: Semaphor '{event_ID}' does not exist.")
        return self.processes[event_ID].overtime(tau_overtime)



