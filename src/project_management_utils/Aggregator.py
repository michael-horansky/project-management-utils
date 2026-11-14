# -----------------------------------------------------------------------------
# ----------------------------- class Aggregator ------------------------------
# -----------------------------------------------------------------------------
# Aggregator collects data tagged by various labels; then, it allows the user
# to extract low-dimensional data by creating aggregation/selection procedures.
#
# Aggregation can propagate errors, but it assumes independence among combined
# parameters etc.

from .color import color
from .Journal import journal
from .Correspondent import Correspondent

from . import PMU_funcs

import numpy as np

str_list_delim = "', '"

class Aggregator_View():

    # Unique hash for aggregation tree leaf values
    _TREE_LEAF = object()

    def __init__(self, agg):
        self.agg = agg

        # We copy the data, reserving a TOTAL_WEIGHT parameter.
        self.data = []
        for dp in self.agg.data:
            mirror_dp = dp.copy()
            mirror_dp["TOTAL_WEIGHT"] = 1
            self.data.append(mirror_dp)

        self.free_params = [p for p in self.agg.parameters.keys()]

    # --------------------- Output and debugging methods ----------------------

    def print_groups(self, redundant_p = None):
        # Groups by all params in redundant_p (can be a single param or a list). Prints the aggregation tree to output.
        # Steps in the aggregation tree which do not branch are contracted to save space.

        if redundant_p is None:
            redundant_p = []
        if isinstance(redundant_p, str):
            redundant_p = [redundant_p]

        if len(redundant_p) != len(set(redundant_p)):
            self.agg.handle_error("Duplicate redundant parameters.")

        unknown = set(redundant_p) - set(self.free_params)
        if unknown:
            self.agg.handle_error(f"Unknown or unavailable parameters: {', '.join(unknown)}")

        aggregation_tags = self.free_params.copy()

        for r_p in redundant_p:
            aggregation_tags.remove(r_p)

        aggregation_tree = {}
        for dp in self.data:
            #if any(dp[r_p] is None for r_p in redundant_p):
            #    continue

            cur_branch = aggregation_tree

            for fp in aggregation_tags:
                if dp[fp] not in cur_branch:
                    cur_branch[dp[fp]] = {}
                cur_branch = cur_branch[dp[fp]]

            # each leaf value is [{r_p : [min value, max value], ...}, total weight]
            if Aggregator_View._TREE_LEAF not in cur_branch:
                # uninitialised leaf
                cur_branch[Aggregator_View._TREE_LEAF] = [{}, dp["TOTAL_WEIGHT"]]
                for r_p in redundant_p:
                    cur_branch[Aggregator_View._TREE_LEAF][0][r_p] = [dp[r_p], dp[r_p]]
            else:
                cur_branch[Aggregator_View._TREE_LEAF][1] += dp["TOTAL_WEIGHT"]
                for r_p in redundant_p:
                    if PMU_funcs.less_than_with_none(dp[r_p], cur_branch[Aggregator_View._TREE_LEAF][0][r_p][0]):
                        cur_branch[Aggregator_View._TREE_LEAF][0][r_p][0] = dp[r_p]
                    if PMU_funcs.more_than_with_none(dp[r_p], cur_branch[Aggregator_View._TREE_LEAF][0][r_p][1]):
                        cur_branch[Aggregator_View._TREE_LEAF][0][r_p][1] = dp[r_p]
        if not aggregation_tree:
            Aggregator.Aggregator_Correspondent.write("Aggregator View empty.")
            return

        def tree_leaf_descriptor(tree_leaf):
            # returns a string
            res = f"{tree_leaf[1]} datapoints"
            if len(redundant_p) == 0:
                return res
            res += "; "
            for r_p in redundant_p:
                res += f"{r_p} from {tree_leaf[0][r_p][0]} to {tree_leaf[0][r_p][1]}, "
            return res[:-2]
        # Now we compress the aggregation tree
        def compressor(cur_branch, cur_depth = 0, key_prefix = ""):
            if cur_depth == len(aggregation_tags):
                if key_prefix == "":
                    return tree_leaf_descriptor(cur_branch[Aggregator_View._TREE_LEAF])
                else:
                    return {key_prefix : tree_leaf_descriptor(cur_branch[Aggregator_View._TREE_LEAF])}
            else:
                cur_p = aggregation_tags[cur_depth]
                if len(cur_branch.keys()) == 1:
                    # No branching, we compress
                    cur_p_val = list(cur_branch.keys())[0]
                    added_key_prefix = f"{cur_p}={cur_p_val}, "
                    return compressor(cur_branch[cur_p_val], cur_depth + 1, key_prefix + added_key_prefix)
                else:
                    res = {}
                    for k in cur_branch.keys():
                        res[key_prefix + f"{cur_p}={k}"] = compressor(cur_branch[k], cur_depth + 1)
                    return res
        output_obj = compressor(aggregation_tree) # standard print_itemize object

        Aggregator.Aggregator_Correspondent.print_itemize(output_obj)



    # -------------------------- aggregation methods --------------------------

    def filter_by_param(self, p, val):
        # Only applicable to error-free parameters
        if p not in self.free_params:
            self.agg.handle_error(f"Unknown filter parameter '{p}'.")
        self.free_params.remove(p)
        if val is None:
            # Only uninitialised values pass
            self.data = [dp for dp in self.data if dp[p] is None]
        else:
            self.data = [dp for dp in self.data if dp[p] is not None and dp[p][0] == val]
        for dp in self.data:
            del dp[p]

    def group_and_aggregate(self, p, redundant_p, f_group):
        # Groups by all params in redundant_p (can be a single param or a list). Applies f_group to the values of p for each group.
        # f_group is a function which takes three arguments in the form of three lists of equal length:
        #   -vals: values of parameter p within each group
        #   -errs: errors on those values
        #   -weights: weight of each datapoint in the group
        #
        # All datapoints for which p or any parameter in redundant_p are
        # uninitialised are ignored.

        if not isinstance(redundant_p, list):
            redundant_p = [redundant_p]

        if p not in self.free_params:
            self.agg.handle_error(f"Unknown aggregation parameter: '{p}'.")

        if p in redundant_p:
            self.agg.handle_error(f"Cannot average over redundant parameter '{p}' (redundant params: '{str_list_delim.join(redundant_p)}').")

        for r_p in redundant_p:
            if r_p not in self.free_params:
                self.agg.handle_error(f"Unknown redundant parameter: '{r_p}'.")

        if len(redundant_p) != len(set(redundant_p)):
            self.agg.handle_error("Duplicate redundant parameters.")

        for r_p in redundant_p:
            self.free_params.remove(r_p)

        aggregation_tags = self.free_params.copy()
        aggregation_tags.remove(p)

        aggregation_tree = {}
        for dp in self.data:
            if dp[p] is None:
                # This datapoint is uninitialised
                continue
            if any(dp[r_p] is None for r_p in redundant_p):
                continue

            cur_branch = aggregation_tree

            for fp in aggregation_tags:
                if dp[fp] not in cur_branch:
                    cur_branch[dp[fp]] = {}
                cur_branch = cur_branch[dp[fp]]

            if p not in cur_branch:
                # uninitialised leaf
                cur_branch[p] = [[], [], []]
            # each leaf value is [values of p, errors on p, total weights]
            cur_branch[p][0].append(dp[p][0])
            cur_branch[p][1].append(dp[p][1])
            cur_branch[p][2].append(dp["TOTAL_WEIGHT"])

        # Empty aggregation tree means no groups were initiated
        if not aggregation_tree:
            self.data = []
            return

        # Now we unwrap the aggregation tree
        def unwrapper(cur_branch, cur_dp = None):
            if cur_dp is None:
                cur_dp = {}
            if len(cur_dp) == len(aggregation_tags):

                new_val, new_err = f_group(*cur_branch[p])
                cur_dp[p] = (new_val, new_err)
                cur_dp["TOTAL_WEIGHT"] = sum(cur_branch[p][2])
                return [cur_dp]
            else:
                res = []
                for k in cur_branch.keys():
                    new_dp = cur_dp.copy()
                    new_dp[aggregation_tags[len(cur_dp)]] = k
                    res.extend(unwrapper(cur_branch[k], new_dp))
                return res
        self.data = unwrapper(aggregation_tree)

    def f_group_average(self, vals, errs, weights):
        # For simplicity, we now ignore errs, as we assume they are artifacts of the distribution from which vals are sampled.
        avg_val = np.average(vals, weights = weights)
        err = np.sqrt(np.average((np.asarray(vals)-avg_val)**2, weights = weights)) # manual calc to keep track of weights
        return (avg_val, err)

    def average_on_param(self, p, redundant_p):
        self.group_and_aggregate(p, redundant_p, self.f_group_average)

    def minimal_satisfying_datapoints_known_threshold(self, p, scoring_p, threshold):

        if p == scoring_p:
            self.agg.handle_error("The aggregation and scoring parameters must be distinct.")
        if p not in self.free_params:
            self.agg.handle_error(f"Unknown aggregation parameter: '{p}'.")
        if scoring_p not in self.free_params:
            self.agg.handle_error(f"Unknown redundant parameter: '{scoring_p}'.")
        self.free_params.remove(scoring_p)

        aggregation_tags = self.free_params.copy()
        aggregation_tags.remove(p)

        aggregation_tree = {}
        for dp in self.data:
            if dp[p] is None or dp[scoring_p] is None:
                # This datapoint is uninitialised
                continue

            cur_branch = aggregation_tree

            for fp in aggregation_tags:
                if dp[fp] not in cur_branch:
                    cur_branch[dp[fp]] = {}
                cur_branch = cur_branch[dp[fp]]

            # each leaf value is [cur val of p, cur total weight]
            if p not in cur_branch:
                # uninitialised leaf
                cur_branch[p] = [None, None, None]

            if dp[scoring_p][0] >= threshold:
                if cur_branch[p][0] is None:
                    # Accept
                    cur_branch[p][0] = dp[p]
                    cur_branch[p][1] = dp["TOTAL_WEIGHT"]
                elif cur_branch[p][0][0] > dp[p][0]:
                    # Accept
                    cur_branch[p][0] = dp[p]
                    cur_branch[p][1] = dp["TOTAL_WEIGHT"]

        # Empty aggregation tree means no groups were initiated
        if not aggregation_tree:
            self.data = []
            return

        # Now we unwrap the aggregation tree. Each group already contains either the correct dp or a None value.
        def unwrapper(cur_branch, cur_dp = None):
            if cur_dp is None:
                cur_dp = {}
            if len(cur_dp) == len(aggregation_tags):

                if cur_branch[p][0] is None:
                    # Empty group
                    return []

                cur_dp[p] = cur_branch[p][0]
                cur_dp["TOTAL_WEIGHT"] = cur_branch[p][1]
                return [cur_dp]
            else:
                res = []
                for k in cur_branch.keys():
                    new_dp = cur_dp.copy()
                    new_dp[aggregation_tags[len(cur_dp)]] = k
                    res.extend(unwrapper(cur_branch[k], new_dp))
                return res
        self.data = unwrapper(aggregation_tree)


    def minimal_satisfying_datapoints(self, p, scoring_p, threshold = None):
        # p, scoring_p are numerical parameters.
        # This method
        #   1. groups data by forgetting p and scoring_p
        #   2. if threshold is not provided:
        #      2.1. in each group, finds the maximal value of scoring_p
        #      2.2. stores the minimum of those maximal values as the threshold
        #   3. in each group, keeps only the datapoint with the smallest value
        #      of p for which the value of scoring_p is not below the threshold
        # This allows us to compare minimal values of p required to bring the
        # scoring_p value over the threshold. The assumption is that increasing
        # p corresponds to increasing scoring_p, but this projection is not
        # required to be strictly monotone.
        #
        # Note: if a threshold is provided, groups which fail to contain any
        # datapoints with scoring_p value over the threshold are ignored.

        if threshold is not None:
            self.minimal_satisfying_datapoints_known_threshold(p, scoring_p, threshold)
            return

        if p == scoring_p:
            self.agg.handle_error("The aggregation and scoring parameters must be distinct.")

        if p not in self.free_params:
            self.agg.handle_error(f"Unknown aggregation parameter: '{p}'.")

        if scoring_p not in self.free_params:
            self.agg.handle_error(f"Unknown redundant parameter: '{scoring_p}'.")
        self.free_params.remove(scoring_p)

        aggregation_tags = self.free_params.copy()
        aggregation_tags.remove(p)

        aggregation_tree = {}
        for dp in self.data:
            if dp[p] is None or dp[scoring_p] is None:
                # This datapoint is uninitialised
                continue

            cur_branch = aggregation_tree

            for fp in aggregation_tags:
                if dp[fp] not in cur_branch:
                    cur_branch[dp[fp]] = {}
                cur_branch = cur_branch[dp[fp]]

            # each leaf value is [vals of p (tupled), vals of scoring_p (only val), total weights]
            if p not in cur_branch:
                # uninitialised leaf
                cur_branch[p] = [[], [], []]
            cur_branch[p][0].append(dp[p])
            cur_branch[p][1].append(dp[scoring_p][0])
            cur_branch[p][2].append(dp["TOTAL_WEIGHT"])

        # Empty aggregation tree means no groups were initiated
        if not aggregation_tree:
            self.data = []
            return

        # We now find the threshold
        def threshold_finder(cur_branch, cur_dp = None):
            if cur_dp is None:
                cur_dp = {}
            if len(cur_dp) == len(aggregation_tags):
                return max(cur_branch[p][1])
            else:
                res = []
                for k in cur_branch.keys():
                    new_dp = cur_dp.copy()
                    new_dp[aggregation_tags[len(cur_dp)]] = k
                    res.append(threshold_finder(cur_branch[k], new_dp))
                return min(res)

        threshold = threshold_finder(aggregation_tree)

        # Now we unwrap the aggregation tree using the found threshold
        def unwrapper(cur_branch, cur_dp = None):
            if cur_dp is None:
                cur_dp = {}
            if len(cur_dp) == len(aggregation_tags):

                cur_best_i = None
                for i in range(len(cur_branch[p][0])):
                    if cur_branch[p][1][i] >= threshold:
                        if cur_best_i is None or cur_branch[p][0][cur_best_i][0] > cur_branch[p][0][i][0]:
                            cur_best_i = i
                if cur_best_i is None:
                    # No satisfying dp found in this group
                    return []

                cur_dp[p] = cur_branch[p][0][cur_best_i]
                cur_dp["TOTAL_WEIGHT"] = cur_branch[p][2][cur_best_i]
                return [cur_dp]
            else:
                res = []
                for k in cur_branch.keys():
                    new_dp = cur_dp.copy()
                    new_dp[aggregation_tags[len(cur_dp)]] = k
                    res.extend(unwrapper(cur_branch[k], new_dp))
                return res
        self.data = unwrapper(aggregation_tree)

    def apply_transformation(self, new_p):
        # Transforms old parameters into new parameter. If this is a reduction (projection), we automatically average the new parameter.
        if new_p not in self.agg.transformations.keys():
            self.agg.handle_error(f"Unknown transformation: '{new_p}'. Available transformations: '{str_list_delim.join(list(self.agg.transformations.keys()))}'.")
        if new_p in self.free_params:
            self.agg.handle_error(f"Transformation '{new_p}' already applied in this view.")
        for rp in self.agg.transformations[new_p]["p"]:
            if rp not in self.free_params:
                self.agg.handle_error(f"Transforming parameter '{rp}' not present in the dataset.")
        for dp in self.data:
            if self.agg.transformations[new_p]["error_sensitive"]:
                cur_args = []
                for rp in self.agg.transformations[new_p]["p"]:
                    cur_args.append(dp[rp])
                    del dp[rp]

                if any(arg is None for arg in cur_args):
                    dp[new_p] = None
                else:
                    dp[new_p] = self.agg.transformations[new_p]["f"](*cur_args)
            else:
                cur_args = []
                for rp in self.agg.transformations[new_p]["p"]:
                    if dp[rp] is not None:
                        cur_args.append(dp[rp][0])
                    else:
                        cur_args.append(None)
                    del dp[rp]

                if any(arg is None for arg in cur_args):
                    dp[new_p] = None
                else:
                    dp[new_p] = (self.agg.transformations[new_p]["f"](*cur_args), 0)

        for rp in self.agg.transformations[new_p]["p"]:
            self.free_params.remove(rp)
        self.free_params.append(new_p)

        if len(self.agg.transformations[new_p]["p"]) > 1:
            self.average_on_param(new_p, []) # empty redundant_p is valid, since there may be automatic redundancy from deleting old parameters


    # -------------------------- Extracting the data --------------------------

    def get_data(self, p):
        # p is a list of parameters we want to keep.
        # We forget all other parameters. Redundancy remains untreated to allow
        # for greater control by the user.
        # The output is a dictionary where each member of p corresponds to a
        # a dict of numpy arrays of values and error values of this member,
        # with matching order between separate members of p.

        if len(p) != len(set(p)):
            self.agg.handle_error("Duplicate parameters requested.")

        output = {}
        if not isinstance(p, list):
            p = [p]
        for param in p:
            output[param] = {"v" : [], "e" : []}
        output["TOTAL_WEIGHT"] = []

        for dp in self.data:
            # If any of the values of members of p is None, we skup this dp.
            if any(dp[param] is None for param in p):
                continue

            for param in p:
                output[param]["v"].append(dp[param][0])
                output[param]["e"].append(dp[param][1])
            output["TOTAL_WEIGHT"].append(dp["TOTAL_WEIGHT"])

        for param in p:
            output[param]["v"] = np.asarray(output[param]["v"])
            output[param]["e"] = np.asarray(output[param]["e"])
        output["TOTAL_WEIGHT"] = np.asarray(output["TOTAL_WEIGHT"])

        return output







class Aggregator():

    reserved_parameters = ["TOTAL_WEIGHT"]

    # Shared correspondent
    Aggregator_Correspondent = Correspondent({"ID" : "AGG", "label" : "Aggregator", "color" : ("cyan", False)}, verbosity_offset = 5)

    @classmethod
    def combine_aggregators(cls, list_of_aggregators):
        # Combines multiple instances of the class into a single large dataset, possibly with a larger parameter list
        res = cls()

        for i in range(len(list_of_aggregators)):
            res.register_parameters(list_of_aggregators[i].parameters, error_on_duplicate = False)
        for i in range(len(list_of_aggregators)):
            res.register_transformations(list_of_aggregators[i].transformations, error_on_duplicate = False)
        for i in range(len(list_of_aggregators)):
            res.add_data(list_of_aggregators[i].data)

        return res


    def __init__(self):

        # Each parameter corresponds to a dimension in the data vector space.

        self.parameters = {} # {param : {"label" : ..., "default" : ...}}

        # Data is stored as a 1D database of rows, where each row assigns a value to each parameter (column).

        self.data = []

        # Transformations are stored functions to derive new parameters from old ones

        self.transformations = {} # "new parameter" : {"p" : old parameters, "f" : transforming function, ...}

        # Unified human-readable labels
        self.label = {}

        # Correspondence with Journal
        self.log = Aggregator.Aggregator_Correspondent

    def handle_error(self, msg, err = ValueError):
        self.log.error(msg)
        raise err(msg)

    # ------------------------ data correction methods ------------------------

    def complete_dp_from_params(self, dp):
        for param in self.parameters.keys():
            if param not in dp.keys():
                if self.parameters[param]["default"] is not None:
                    dp[param] = (self.parameters[param]["default"], 0)
                else:
                    # Missing value
                    dp[param] = None

    def complete_data_from_params(self):
        for dp in self.data:
            self.complete_dp_from_params(dp)


    # ------------ parameter/datapoint/transformation registration ------------

    def register_label(self, name, label):
        self.label[name] = label

    def register_parameter(self, name, label = None, default = None):
        if name in Aggregator.reserved_parameters:
            self.handle_error(f"Parameter name '{name}' is reserved.")

        if name in self.parameters:
            if error_on_duplicate:
                self.handle_error(f"Attempting registration of duplicate parameter '{name}'.")
            else:
                self.log.warning(f"Duplicate parameter '{name}' encountered. Skipping the reassignment.", 10)
                return

        # If no label is given, we just use the param name
        if label is None:
            label = name
        self.parameters[name] = {"label" : label, "default" : default}
        self.register_label(name, label)

    def register_parameters(self, p, error_on_duplicate = True):
        # p is in the form {param : {"label" : ..., "default" : ...}}
        for p_name, p_props in p.items():
            self.register_parameter(p_name, p_props.get("label", None), p_props.get("default", None))

    def register_transformation(self, new_p, old_ps, f_trans, label = None, error_sensitive = False, error_on_duplicate = True):
        # new_p is name of new parameter
        # old_ps is list of old parameters which transform and thus are aggregated into new_p
        # f_trans is a function old_ps -> new_p
        #
        # If error_sensitive, each argument and the output have the form (val, err)
        # Otherwise, they are simply numerical values.
        if new_p in self.transformations.keys():
            if error_on_duplicate:
                self.handle_error(f"Derived parameter '{new_p}' already registered with a transformation.")
            else:
                self.log.warning(f"Duplicate derived parameter '{new_p}' encountered. Skipping the reassignment.", 10)
                return
        if new_p in self.parameters.keys():
            self.handle_error(f"Derived parameter '{new_p}' already present in registered parameters.")
        if new_p in Aggregator.reserved_parameters:
            self.handle_error(f"Derived parameter '{new_p}' is already a reserved parameter.")

        if isinstance(old_ps, str):
            old_ps = [old_ps]
        else:
            old_ps = list(old_ps)

        if not old_ps:
            self.handle_error("Transformation requires at least one argument.")

        if len(old_ps) != len(set(old_ps)):
            self.handle_error("Duplicate transformation arguments.")

        if label is None:
            label = new_p

        self.transformations[new_p] = {"p" : old_ps, "f" : f_trans, "label" : label, "error_sensitive" : error_sensitive}
        self.register_label(new_p, label)

    def register_transformations(self, new_trans, error_on_duplicate = True):
        for new_p, new_p_props in new_trans.items():
            self.register_transformation(new_p, new_p_props["p"], new_p_props["f"], label = new_p_props["label"], error_sensitive = new_p_props.get("error_sensitive", False), error_on_duplicate = error_on_duplicate)


    def add_dp(self, dp):
        # Adds datapoint.
        # dp is in the form {param : polymorph object, ...}
        # where the polymorph object can take the following forms:
        #   -None. Missing value.
        #   -value. Error is assumed to be 0.
        #   -(value, error)
        #   -{"v": value, "e" : error}
        # This process brings the datapoint to the standard form 2 (+ 0).

        # First, we check if there are parameters which are not registered
        dp = dp.copy()
        for param in dp.keys():
            if param not in self.parameters.keys():
                self.register_parameters({param : {}})

        self.complete_dp_from_params(dp)

        # We standardise the form of dp
        std_dp = {}
        for param, val in dp.items():
            if val is None:
                # Missing value.
                std_dp[param] = None
            elif isinstance(val, dict):
                if "v" not in val:
                    self.handle_error("Dictionary values forbidden; please flatten them into sequenced parameters.")
                std_dp[param] = (val["v"], val.get("e", 0))
            elif isinstance(val, tuple):
                if len(val) != 2:
                    self.handle_error("Tuple values forbidden; please flatten them into sequenced parameters.")
                std_dp[param] = val
            else:
                std_dp[param] = (val, 0)
        self.data.append(std_dp)

    def add_data(self, new_data):
        for new_dp in new_data:
            self.add_dp(new_dp)

    # ---------------------------- view management ----------------------------

    def create_view(self):
        return(Aggregator_View(self))

    # ------------------------ Aggregator composition -------------------------

    def __add__(self, other):
        return Aggregator.combine_aggregators([self, other])



