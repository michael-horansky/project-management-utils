# A simple class which allows conditional access to a Journal instance if provided with one.

class Correspondent:

    def __init__(self, journal_instance = None, agent = None, verbosity_offset = None):
        self.journal_instance = journal_instance

        self.agent = agent # Either None or a dict with keywords "ID", "label", "color"
        self.agent_ID = None

        if self.journal_instance is not None and self.agent is not None:
            if not isinstance(self.agent, dict):
                raise Exception(f"Agent must be a dict; provided agent is of type {type(self.agent)}.")
            for req_key in ["ID", "label", "color"]:
                if req_key not in self.agent:
                    raise Exception(f"'{req_key}' is a required key in agent.")

            # We register a new agent
            self.journal_instance.register_agent_tag(self.agent["ID"], {"label" : self.agent["label"], "color" : self.agent["color"]})
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
        if self.journal_instance is not None:
            self.journal_instance.write(msg, v, agent = self.agent_ID)

    def enter(self, msg, v = None):
        v = self.reassure_verbosity(v)
        if self.journal_instance is not None:
            self.journal_instance.enter(msg, v, agent = self.agent_ID)

    def exit(self):
        if self.journal_instance is not None:
            self.journal_instance.exit()

    def warning(self, msg, v = -1):
        if self.journal_instance is not None:
            self.journal_instance.warning(msg, v, agent = self.agent_ID)

    def error(self, msg, v = -1):
        if self.journal_instance is not None:
            self.journal_instance.error(msg, v, agent = self.agent_ID)

    def ask_yes_no(self, msg, default):
        if self.journal_instance is not None:
            return(self.journal_instance.ask_yes_no(msg, agent = self.agent_ID))
        return(default)

    def print_itemize(self, std_object):
        if self.journal_instance is not None:
            self.journal_instance.print_itemize(std_object, agent = self.agent_ID)
