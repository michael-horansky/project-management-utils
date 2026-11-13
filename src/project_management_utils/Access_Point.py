# Each object is a simple header which specifies the arguments for a given
# Access Point (AP) script. It handles typing and input errors.

import sys

from .Correspondent import Correspondent

class Access_Point():

    AP_Correspondent = Correspondent({"ID" : "AP", "label" : "Access Point", "color" : "red"})

    reserved_args = ["man", "help", "reserved"]

    def __init__(self, name, desc, params):
        # name is a short string; the filename of the script
        # desc is a long description of what the script does
        # params is a list in the form [i] = [label, type, default value, desc]
        #     -label is a short string; the name of the parameter
        #     -type is a class, and the input gets re-typed using the provided
        #      class
        #     -if the parameter is missing and default value is not None, the
        #      default value is used instead. The general structure must adhere
        #      to [mandatory arguments ... optional arguments ...]
        #     -desc is a string, and describes the purpose of the parameter
        self.name = name
        self.desc = desc
        self.params = params

        self.param_names = []
        for i in range(len(self.params)):
            if self.params[i][0] in Access_Point.reserved_args:
                # Trying to use a reserved param name
                Access_Point.AP_Correspondent.error(f"Access Point cannot be initialised with a parameter called '{self.params[i][0]}'; this name is reserved for special arguments.")

            self.param_names.append(self.params[i][0])

    def enforce_type(self, i, val):
        try:
            return(self.params[i][1](val))
        except:
            Access_Point.AP_Correspondent.error(f"Conversion of parameter \"{self.params[i][0]}\" failed (type \"{str(self.params[i][1])}\" expected; provided value {val} is of type {type(val)})", err = TypeError)

    def process_reserved_arg(self, arg):
        # Certain reserved args may result in raising exceptions or otherwise disrupting the flow of the program.
        if arg in ["man", "help"]:
            self.man()
            quit()
        if arg in ["reserved"]:
            self.print_reserved_args()
            quit()

    def process_cmd_args(self):
        # Returns a dict of properly-typed arguments if cmd_args is sane
        # Raises an error and returns None if cmd_args is ill-formed

        cmd_args = sys.argv[1:]

        res = {}

        Access_Point.AP_Correspondent.enter("Processing command parameters...")

        # We split the positional and keyword arguments

        args_pos = []
        args_kw = {}

        initialised_params = []

        kw_arg_encountered = False
        for i in range(len(cmd_args)):
            if cmd_args[i] in Access_Point.reserved_args:
                # arg was processed as a reserved arg. Skipping to next arg.
                self.process_reserved_arg(cmd_args[i])
            elif "=" in cmd_args[i]:
                key, value = cmd_args[i].split("=", 1)
                if key not in self.param_names:
                    raise Exception(f"Unknown keyword argument \"{key}\" (provided value {value}).")
                param_index = self.param_names.index(key)
                if param_index in initialised_params:
                    raise Exception(f"Keyword argument \"{key}\" has encountered duplicate value assignment.")
                initialised_params.append(param_index)
                args_kw[key] = value
                kw_arg_encountered = True
            elif kw_arg_encountered:
                raise Exception(f"Positional argument (i. {i + 1}, val. {cmd_args[i]}) encountered after a keyword argument. Please use the format [positional arguments] [keyword arguments].")
            else:
                args_pos.append(cmd_args[i])
                initialised_params.append(i)


        for i in range(len(args_pos)):
            res[self.param_names[i]] = self.enforce_type(i, args_pos[i])
            Access_Point.AP_Correspondent.write(f"\"{self.params[i][0]}\" set to {res[self.param_names[i]]}")

        for i in range(len(args_pos), len(self.params)):

            if self.param_names[i] in args_kw.keys():
                res[self.param_names[i]] = self.enforce_type(i, args_kw[self.param_names[i]])
                Access_Point.AP_Correspondent.write(f"\"{self.param_names[i]}\" set to {res[self.param_names[i]]}")

            elif self.params[i][2] is None:
                Access_Point.AP_Correspondent.error(f"Parameter \"{self.params[i][0]}\" mandatory but not provided (parameter index {i}).")
            else:
                res[self.param_names[i]] = self.params[i][2]
                Access_Point.AP_Correspondent.write(f"\"{self.param_names[i]}\" defaulted to {res[self.param_names[i]]}")
        Access_Point.AP_Correspondent.exit()
        return(res)

    def man(self):
        # Prints the manual for the access point, i.e. the required parameters
        Access_Point.AP_Correspondent.enter("This is a computation access point.")
        Access_Point.AP_Correspondent.write(f"Script name: {self.name}")
        Access_Point.AP_Correspondent.print_paragraph(self.desc, line_width = 80)
        Access_Point.AP_Correspondent.print_dinkus(w = 80)

        params_obj = {}
        for i in range(len(self.params)):
            if self.params[i][2] is None:
                params_obj[f"\"{self.params[i][0]}\" [{str(self.params[i][1])}]"] = self.params[i][3]
            else:
                params_obj[f"\"{self.params[i][0]}\" [{str(self.params[i][1])}] (default {str(self.params[i][2])})"] = self.params[i][3]
        Access_Point.AP_Correspondent.write("Parameters:")
        Access_Point.AP_Correspondent.print_itemize(params_obj)

        # TODO add wrap_at_w = [None, none, 80] param to print_table so we can make certain cells wrap text to multi lines
        """param_table_name = "Parameters"
        param_table_cols = ["type", "default", "description"]
        param_table_rows = []
        param_table_data = []

        for i in range(len(self.params)):
            param_table_rows.append(self.params[i][0])
            param_table_data.append([str(self.params[i][1]), "" if self.params[i][2] is None else str(self.params[i][2]), self.params[i][3]])

        Access_Point.AP_Correspondent.print_table(param_table_name, param_table_cols, param_table_rows, param_table_data)"""

        """

        Access_Point.AP_Correspondent.write("Parameters:")
        for i in range(len(self.params)):
            if self.params[i][2] is None:
                print(f"  \"{self.params[i][0]}\" [{str(self.params[i][1])}]: {self.params[i][3]}")
            else:
                print(f"  \"{self.params[i][0]}\" [{str(self.params[i][1])}] (default {str(self.params[i][2])}): {self.params[i][3]}")
        """
        Access_Point.AP_Correspondent.exit()

    def print_reserved_args(self):
        Access_Point.AP_Correspondent.write("The following arguments are reserved for special actions:")

        Access_Point.AP_Correspondent.print_itemize({
                "'man', 'help'" : "the full parameter list for the current access point is displayed; the program terminates.",
                "'reserved'" : "the list of reserved arguments is displayed; the program terminates."
            })

        #print("  'man', 'help': the full parameter list for the current access point is displayed; the program terminates.")
        #print("  'reserved': the list of reserved arguments is displayed; the program terminates.")


