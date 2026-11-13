# A simple class which allows conditional access to a Journal instance if provided with one.

from .Journal import journal

class Correspondent:

    def __init__(self, agent = None, verbosity_offset = None):

        self.agent = agent # Either None or a dict with keywords "ID", "label", "color"
        self.agent_ID = None

        if self.agent is not None:
            if not isinstance(self.agent, dict):
                raise Exception(f"Agent must be a dict; provided agent is of type {type(self.agent)}.")
            for req_key in ["ID", "label", "color"]:
                if req_key not in self.agent:
                    raise Exception(f"'{req_key}' is a required key in agent.")

            # We register a new agent
            journal.register_agent_tag(self.agent["ID"], {"label" : self.agent["label"], "color" : self.agent["color"]})
            self.agent_ID = self.agent["ID"]

        self.verbosity_offset = verbosity_offset # Applied to write and enter, not warning or error.

    # Default verbosity calculation
    def reassure_verbosity(self, v):
        if v is None:
            if self.verbosity_offset is None:
                return(-1)
            return(self.verbosity_offset)
        return(v)

    # -------------- Journal methods ---------------
    def write(self, msg, v = None):
        v = self.reassure_verbosity(v)
        if journal is not None:
            journal.write(msg, v, agent = self.agent_ID)

    def enter(self, msg, v = None):
        v = self.reassure_verbosity(v)
        if journal is not None:
            journal.enter(msg, v, agent = self.agent_ID)

    def exit(self):
        if journal is not None:
            journal.exit()

    # ---------------------- Semaphor management methods ----------------------

    def semaphor_update(self, tau, S_ID = None):
        if journal is not None:
            journal.semaphor_update(tau, S_ID = S_ID)

    def semaphor_progress(self, tau_progress = 1, S_ID = None):
        if journal is not None:
            journal.semaphor_progress(tau_progress = tau_progress, S_ID = S_ID)

    def semaphor_overtime(self, tau_overtime = 1, S_ID = None):
        if journal is not None:
            journal.semaphor_overtime(tau_overtime = tau_overtime, S_ID = S_ID)

    # -------------------- Special object printing methods --------------------

    def warning(self, msg, v = -1):
        if journal is not None:
            journal.warning(msg, v, agent = self.agent_ID)

    def error(self, msg, v = -1, err = ValueError):
        if journal is not None:
            journal.error(msg, v, agent = self.agent_ID, err = err)

    def print_itemize(self, std_object, v = -1):
        if journal is not None:
            journal.print_itemize(std_object, agent = self.agent_ID)

    def print_matrix(self, m, label, dec_points = 5, max_rows = 11, v = -1):
        if journal is not None:
            journal.print_matrix(m, label, dec_points = dec_points, max_rows = max_rows, v = v, agent = self.agent_ID)

    def print_table(self, table_name, column_names, row_names, list_of_rows, subtable_borders = [], header_separation = 2, v = -1, agent = None):
        if journal is not None:
            journal.print_table(table_name, column_names, row_names, list_of_rows, subtable_borders = subtable_borders, header_separation = header_separation, v = v, agent = self.agent_ID)

    def print_paragraph(self, msg, line_width = None, v = -1, n = 6):
        if journal is not None:
            journal.print_paragraph(msg, line_width = line_width, v = v, agent = self.agent_ID, n = n)

    def print_dinkus(self, w = None, v = -1):
        if journal is not None:
            journal.print_dinkus(w = w, v = v, agent = self.agent_ID)

    # -------------------------- Interactive prompts --------------------------

    def ask_yes_no(self, msg, default):
        if journal is not None:
            return(journal.ask_yes_no(msg, agent = self.agent_ID))
        return(default)
