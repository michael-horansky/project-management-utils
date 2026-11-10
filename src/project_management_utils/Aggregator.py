# -----------------------------------------------------------------------------
# ----------------------------- class Aggregator ------------------------------
# -----------------------------------------------------------------------------
# Aggregator collects data tagged by various labels; then, it allows the user
# to extract low-dimensional data by creating aggregation/selection procedures.


from .color import color
from .Correspondent import Correspondent

class Aggregator():

    @classmethod
    def combine_aggregators(cls, list_of_aggregators):
        # Combines multiple instances of the class into a single large dataset, possibly with a larger parameter list
        pass

    def __init__(self):

        # Each parameter corresponds to a dimension in the data vector space.

        self.parameters = {} # {param : {"label" : ..., "default" : ...}}

        # Data is stored as a 1D database of rows, where each row assigns a value to each parameter (column).

        self.data = []

        # Correspondence with Journal
        self.log = Correspondent(journal_instance, {"ID" : "AGG", "label" : "Aggregator", "color" : color.CYAN}, verbosity_offset = 5)

    def add_dp(self, dp):
        # Adds datapoint.
        # dp is in the form {param : value, ...}


