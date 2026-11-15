from . import PMU_funcs

from .color import color
from .Printable_Semaphor import Printable_Semaphor

# -----------------------------------------------------------------------------
# -------------------------- Typographical constants --------------------------
# -----------------------------------------------------------------------------

# ---------------------------------- Colors -----------------------------------



# -----------------------------------------------------------------------------
# ------------------------------- class Journal -------------------------------
# -----------------------------------------------------------------------------

class Journal():

    # ------------------------ Typographical constants ------------------------

    pipe = "| "
    asterism = " * * * "

    gradual_fg_color = [ # used for pipes. Highlights routine depth. Cycles.
            color.BRIGHT_BLUE,
            color.BRIGHT_MAGENTA,
            color.CYAN,
            color.BRIGHT_CYAN
        ]

    # --------------------------- Class properties ----------------------------

    time_format = "%H:%M:%S" # Print time with

    answer_strings = {
        "yes" : ["yes", "y", "aye"],
        "no" : ["no", "n"]
        }

    valid_answers = []
    for a_val in answer_strings.values():
        valid_answers += a_val

    @classmethod
    def sample_behaviour(cls, **kwargs):
        # useful when testing whether behaviour is as expected
        sample_journal = cls(**kwargs)

        sample_journal.enter("Journal behaviour test commences...")
        sample_journal.write("This is a sample instance of class Journal. Please take note of when the announced function does not agree with the output.")

        sample_journal.enter("Testing special object printing methods...")
        sample_journal.write("Special objects, such as item lists, tables, or matrices, can be printed with special formatting using these methods.")

        sample_journal.warning("This is a sample warning.")
        sample_journal.error("This is a sample error.", err = None)

        sample_journal.enter("Testing item list printing...")
        sample_journal.print_itemize({
            "print_itemize" : "Prints an itemized/enumerated list from a standard object. Supports nested lists. Max width can be specified.",
            "nested numbered list (list)" : ["First element", "Second element", {"this" : "First part of third element", "that" : "Second part of third element"}, "Fourth element"],
            "nested labelled list (dict)" : {"Keyword" : "Value", "Other keyword" : "Other value"},
            "nested itemized list (tuple)" : ("Tuples are immutable...", ["Nested numbered list here!", "Nesting iterables inside itemized lists doesn't really look good due to the dangling dash.", "Don't forget the trailing space when creating a single-element tuple!"], "...but they can contain references to mutable objects, so don't worry about nesting other iterables inside them.")
            }, w = 80)
        sample_journal.exit()

        sample_journal.enter("Testing matrix printing...")
        sample_journal.print_matrix(
            [[0.5 + 1j] * 5, [0.554 + 0.518j] * 5, [0.245] * 5, [0.5 - 0.5j] * 5, [0.5 - 1j] * 5],
            "Example matrix",
            2,
            4
            )
        sample_journal.exit()

        sample_journal.enter("Testing table printing...")
        sample_journal.print_table(
            table_name = "Current properties",
            column_names = ["value", "default", "description"],
            row_names = ["verbosity", "print_on_the_fly", "fancy_printing", "max_row_width", "yes"],
            list_of_rows = [
                [sample_journal.verbosity, 5, "Only logs with lower or equal value of verbosity are printed."],
                [sample_journal.print_on_the_fly, "True", "Whether the log is also printed to an output stream."],
                [sample_journal.fancy_printing, "True", "Formatting: font weight and color, rolling last line."],
                [sample_journal.max_row_width, 200, "Rows get trimmed if length exceeds this value."],
                [sample_journal.yes, None, "If not None, used instead of asking for input."]
                ],
            subtable_borders=[1]
            )
        sample_journal.exit()

        sample_journal.exit()

        sample_journal.enter("Testing semaphors...")
        sample_journal.write("Semaphor is used to update the user periodically when the program spends a long time on one task.")

        sample_journal.enter("Calculating gibberish", semaphored = True, label = 'Babble', tau_space = (100, 100))

        for a in range(10):
            for b in range(10):
                # We do something very computationally heavy here, I think

                total = 0
                for i in range(1000):
                    for j in range(1000):
                        total += ((i + a) * (j + b)) % 97

                sample_journal.semaphor_progress()
                # Don't forget to update the semaphor with the current sim time!

        duration = sample_journal.exit()

        sample_journal.exit()

        sample_journal.enter("Testing user input collection...")
        sample_journal.write("The journal can ask yes/no questions. This pauses the program. Set the 'yes' property to assume the answers.")
        ans = sample_journal.ask_yes_no("Is this true?")
        if ans:
            sample_journal.write("The user has decided that this is true.")
        else:
            sample_journal.write("The user has decided that this is false.")
        sample_journal.exit()

        sample_journal.exit()
        sample_journal.close_journal()

        print(sample_journal.dump())


    # -------------------- Constructor, descriptor, output --------------------

    def __init__(self, verbosity = 5, print_on_the_fly = True, fancy_printing = True, max_row_width = 200, yes = None):

        # Verbosity key:
        #   0/None: Important, always prints (user methods)
        #   2: Important, major subroutine
        #   5: Minor subroutine
        #   10: Micro-subroutine (expected to repeat many times)
        # Typically, writes within subroutines are one level of verbosity higher than the subroutine itself

        self.journal_text = ""
        self.routine_stack = [] # every routine is [header, max required verbosity, agent, associated semaphor ID]
        self.depth = 0

        self.set_verbosity(verbosity) # The higher the verbosity, the more in detail the Journal is
        self.set_print_on_the_fly(print_on_the_fly) # If True, printing to terminal happens concurrently
        self.set_fancy_printing(fancy_printing) # if True, we use colors, highlighting etc
        self.set_max_row_width(max_row_width) # used for clever wrapping
        self.set_yes(yes) # If not None, used instead of asking for input

        self.last_printed_line = None # Always printed with \r until next line is staged, with different colour
        self.last_printed_line_no_temp = None # Sometimes we trim the line to make space for temporary elements. When that happens, we store the less trimmed version to print when committing the line.
        self.last_printed_depth = 0
        self.last_printed_padding = 0 # The padding required when committing the no temp line. = padding_length at preview - (len(plain no temp last line) - len(plain last line))
        self.last_printed_temporary_elements = None

        self.semaphor = Printable_Semaphor() # The in-house semaphor used to hang on a routine
        self.cur_semaphor_event = None
        self.cur_semaphor_prefix_id = 0

        self.agent_tags = {} # Used to distinguish write sources. Each tag has the form "agent" : {"label" : "agent name", "color" : "color code"}
        self.stack_agent = None

    # --------------- Post-initialisation parameter assignment ----------------

    def set_verbosity(self, v):
        if not isinstance(v, int) or v < 0:
            raise ValueError("Verbosity must be set to a non-negative integer value.")
        self.verbosity = v

    def set_print_on_the_fly(self, print_on_the_fly):
        if not isinstance(print_on_the_fly, bool):
            raise ValueError("'Print on the fly' must be set to a boolean value.")
        self.print_on_the_fly = print_on_the_fly

    def set_fancy_printing(self, fancy_printing):
        if not isinstance(fancy_printing, bool):
            raise ValueError("'Fancy printing' must be set to a boolean value.")
        self.fancy_printing = fancy_printing

    def set_max_row_width(self, max_row_width):
        if not isinstance(max_row_width, int) or max_row_width < 10:
            raise ValueError("'Maximal row width' must be set to an integer value greater than 9.")
        self.max_row_width = max_row_width

    def set_yes(self, yes):
        if not isinstance(yes, bool) and yes is not None:
            raise ValueError("'yes' must be set to a boolean value or to None.")
        self.yes = yes

    def close_journal(self):

        w = self.max_allowed_w(80)

        while(self.depth > 0):
            self.exit()

        fancy_endline = PMU_funcs.st(color.bold(color.fg_highlight('green', " Process finished ", True)), w, '-', plain_len = 18)
        plain_endline = PMU_funcs.st(" Process finished ", w, '-', plain_len = 18)
        self.write_line(fancy_endline, plain_msg = plain_endline, temporary_elements = False)

        if self.print_on_the_fly and self.fancy_printing:
            self.commit_last_line()

    def dump(self, erase_journal_text = True):
        # dumps journal into string, resetting it to empty otherwise disabled
        res = self.journal_text
        if erase_journal_text:
            self.journal_text = ""
        return(res)

    # ----------------------------- Text wrapping -----------------------------

    def max_allowed_w(self, w = None):
        if w is None:
            return max(0, self.max_row_width - self.depth * len(Journal.pipe))
        else:
            return max(0, min(self.max_row_width - self.depth * len(Journal.pipe), w))

    # --------------------- Temporary elements management ---------------------

    def get_temporary_elements_width(self):
        # Temporary elements are elements automatically added to the preprint
        # (i.e. highlight line), but do not persist in the output. As such,
        # they must be overlaid with a padding when committing lines.
        # This method calculates the exact width of that padding.

        # Temporary element: progress bars
        return self.semaphor.padding_length

    def get_temporary_elements(self):
        res = ""
        if len(self.semaphor.processes) > 0:
            res += self.semaphor.progress_bars(self.fancy_printing)
        return res

    # --------------------------- Prefix management ---------------------------

    def pipe_stack(self, n, allow_fancy = True):
        if self.fancy_printing and allow_fancy:
            res = ""
            for i in range(n):
                res += Journal.gradual_fg_color[i % len(Journal.gradual_fg_color)] + Journal.pipe + color.END
            return(res)
        else:
            return(Journal.pipe * n)

    def pre(self, allow_fancy = True, enforce_depth = None, temporary_elements = True):
        # prefix for current depth.

        if enforce_depth is None:
            enforce_depth = self.depth

        # The general form is [pipes] [temporary elements (in highlight only)]
        res = self.pipe_stack(enforce_depth, allow_fancy)
        if temporary_elements and self.fancy_printing and allow_fancy:
            res += self.get_temporary_elements()
        return res

    def get_exit_pre(self):
        plain_exit_pre = "\\_ "
        if self.fancy_printing:
            fancy_exit_pre = Journal.gradual_fg_color[self.depth % len(Journal.gradual_fg_color)] + "\\_" + color.END + " "
        else:
            fancy_exit_pre = plain_exit_pre
        return (fancy_exit_pre, plain_exit_pre)

    def get_stack_v(self):
        # If stack is non-empty, we return last max req verbosity from stack; -1 otherwise (no requirement)
        if len(self.routine_stack) > 0:
            return(self.routine_stack[-1][1])
        return(-1)

    def update_stack_agent(self):
        if len(self.routine_stack) > 0:
            self.stack_agent = self.routine_stack[-1][2]
        else:
            self.stack_agent = None

    # ------------------------ Fancy printing methods -------------------------

    def commit_last_line(self):
        if self.last_printed_line_no_temp is not None:
            print(self.pipe_stack(self.last_printed_depth) + self.last_printed_line_no_temp + ' ' * self.last_printed_padding)
            self.last_printed_line = None
            self.last_printed_line_no_temp = None
            self.last_printed_depth = 0
            self.last_printed_padding = 0
            self.last_printed_temporary_elements = None

    def preview_print(self, msg, update_preview = True, temporary_elements = True, msg_no_temp = None, msg_no_temp_diff = 0):
        # If fancy printing is enabled, we always pre-print the last line in bold
        if update_preview:
            self.last_printed_line = msg
            self.last_printed_line_no_temp = msg_no_temp if msg_no_temp is not None else msg
            self.last_printed_depth = self.depth
            self.last_printed_padding = max(0, (self.get_temporary_elements_width() if temporary_elements else 0) - msg_no_temp_diff)
            self.last_printed_temporary_elements = temporary_elements
        print(self.pre(enforce_depth = self.last_printed_depth, temporary_elements = temporary_elements) + color.bold(msg), end="\r")

    def reload_preview(self):
        if self.print_on_the_fly and self.fancy_printing and self.last_printed_line is not None:
            self.preview_print(self.last_printed_line, update_preview = False, temporary_elements = self.last_printed_temporary_elements)

    # ----------------------------- Write method ------------------------------

    def write_line(self, msg, v = -1, prevent_printing_on_the_fly = False, record_to_journal = True, plain_msg = None, agent = None, temporary_elements = True, is_exit = False):
        # Internal method to display message for which both fancy text and
        # plaintext are known.
        # This method simply prints one line.

        if self.verbosity < max(v, self.get_stack_v()):
            return

        w = self.max_allowed_w()
        temp_w = 0

        # If this is an exit, we must reserve three characters for the exit pre
        if is_exit:
            w -= 3

        # If we can't fit the temporary elements, we disable them
        if self.get_temporary_elements_width() > w:
            temporary_elements = False
        else:
            # We print temporary elements, which means we need to make space for them
            temp_w = self.get_temporary_elements_width()

        if plain_msg is None:
            plain_msg = msg

        agent_pre, agent_plain_pre = self.get_agent_tag(agent)
        msg = agent_pre + msg
        plain_msg = agent_plain_pre + plain_msg
        msg_no_temp = msg
        msg_no_temp_diff = 0

        # Trimming to respect max row width
        if len(plain_msg) > w:
            # We print the plain message aggressively trimmed.
            msg = plain_msg[:max(0, w - temp_w)]
            msg_no_temp = plain_msg[:w]
            msg_no_temp_diff = w - max(0, w - temp_w)
            plain_msg = plain_msg[:w]
        elif len(plain_msg) > max(0, w - temp_w):
            # The no temp message is untrimmed, but the preview message is trimmed
            msg = plain_msg[:max(0, w - temp_w)]
            msg_no_temp_diff = len(plain_msg) - max(0, w - temp_w)

        if is_exit:
            # We now attach the exit pre
            fancy_exit_pre, plain_exit_pre = self.get_exit_pre()
            msg = fancy_exit_pre + msg
            msg_no_temp = fancy_exit_pre + msg_no_temp
            plain_msg = plain_exit_pre + plain_msg

        if record_to_journal:
            self.journal_text += self.pre(allow_fancy = False) + plain_msg + "\n"
        if self.print_on_the_fly and not prevent_printing_on_the_fly:
            if self.fancy_printing:
                # We firstly print the last submitted line, and then the preprint of the current line
                self.commit_last_line()
                self.preview_print(msg, temporary_elements = temporary_elements, msg_no_temp = msg_no_temp, msg_no_temp_diff = msg_no_temp_diff)
            else:
                # crude printing only
                print(self.pre(allow_fancy = False) + plain_msg)


    def write(self, msg, v = -1, w = None, n = 6, min_w = None, prevent_printing_on_the_fly = False, agent = None, temporary_elements = True):
        # Writes a message inside current routine at current depth
        # Arguments:
        #   -msg: Text to be printed. Crudely converted to string if needed.
        #         Must be plaintext (no ANSI escape codes).
        #   -v: verbosity. Only prints if lower than system verbosity.
        #   -w: Maximum width of the output, in characters.
        #   -n: How many characters can be pushed from end of one line to the
        #       start of the next one to prevent linebreaking inside words.
        #   -min_w: Minimum width of the output, in characters. If the value of
        #           w drops below min_w, no printing occurs.
        #   -prevent_printing_on_the_fly: Recorded to the Journal text, but not
        #                                 displayed in the output.
        #   -agent: Agent ID of write author. Agent tag is added conditionally.
        #   -temporary_elements: Whether to include them. Set to False only for
        #                        multi-line batches of pre-computed text.
        #   -padding_length: How much padding is printed on the right side of
        #                    the message (to erase temporary elements).

        # Only input padding_length manually when the length needs to be
        # reserved before altering the semaphor status (like on finishing
        # semaphor events).

        msg = str(msg)

        if "\x1b" in msg:
            self.error("Input to the write method must not contain ANSI escape characters.")

        if self.verbosity < max(v, self.get_stack_v()):
            return

        # Normalise arguments
        agent_pre, agent_plain_pre = self.get_agent_tag(agent)
        temp_w = self.get_temporary_elements_width()
        w = self.max_allowed_w(w)
        if min_w is None:
            # We must be allowed to print an asterism or the agent tag unbroken
            min_w = max(len(Journal.asterism), len(agent_plain_pre))
        # We must reserve space for all temporary elements
        if w < temp_w:
            temporary_elements = False
            temp_w = 0
        if  w < min_w + temp_w:
            # No wrapping, just a trim
            self.journal_text += self.pre(allow_fancy = False) + msg[:w] + "\n"
            if self.print_on_the_fly and not prevent_printing_on_the_fly:
                if self.fancy_printing:
                    # We firstly print the last submitted line
                    self.commit_last_line()
                    self.preview_print(msg[:w - temp_w], temporary_elements = temporary_elements)
                else:
                    # crude printing only
                    print(self.pre(allow_fancy = False) + msg[:w])
            return

        # We firstly append the plain agent tag placeholder to msg in order to
        # properly wrap it.
        # Non-empty agent tags always end with a trailing space, which
        # ensures we can linebreak on that space if necessary.
        msg = agent_plain_pre + msg

        sequenced_msg = PMU_funcs.wrap_text(msg, w, min_w, hyphenate = True, n = n)

        # Now we write the message line by line to plaintext journal.
        for i in range(len(sequenced_msg)):
            self.journal_text += self.pre(allow_fancy = False) + sequenced_msg[i] + "\n"

        if not sequenced_msg:
            return

        # We now reserve enough space in the last line for the temporary
        # elements. If there isn't enough space, we add an empty line to the
        # end, which will simply display the temporary elements.
        if len(sequenced_msg[-1]) > w - temp_w:
            sequenced_msg.append("")

        # We now make the agent pre fancy
        if self.fancy_printing:
            sequenced_msg[0] = agent_pre + sequenced_msg[0][len(agent_plain_pre):]

        if self.print_on_the_fly and not prevent_printing_on_the_fly:
            if self.fancy_printing:
                # We firstly print the last submitted line
                self.commit_last_line()

                for i in range(len(sequenced_msg) - 1):
                    print(self.pre(temporary_elements = False) + sequenced_msg[i])

                self.preview_print(sequenced_msg[-1], temporary_elements = temporary_elements)
            else:
                # crude printing only
                for i in range(len(sequenced_msg)):
                    print(self.pre(allow_fancy = False) + sequenced_msg[i])

    # -------------------- Special object printing methods --------------------

    def print_precomputed_batch(self, fancy_lines, plain_lines, v = -1, agent = None):
        # If agent needs to be printed, we print it on the top
        agent_pre, agent_plain_pre = self.get_agent_tag(agent)
        if agent_plain_pre:
            self.write_line("", v = v, agent = agent, temporary_elements = False)

        if len(fancy_lines) == 0:
            # fancy lines were not initialised
            for i in range(len(plain_lines)):
                self.write_line(plain_lines[i], v = v, agent = None, temporary_elements = False)
        else:
            for i in range(len(plain_lines)):
                self.write_line(fancy_lines[i], v = v, plain_msg = plain_lines[i], agent = None, temporary_elements = False)

        # If temporary elements need to be printed, we print them here
        if self.get_temporary_elements_width() > 0:
            self.write_line("", v = v, record_to_journal = False, agent = None)

    def warning(self, msg, v = -1, agent = None):
        fancy_msg = color.BRIGHT_YELLOW + color.BOLD + "WARNING" + color.END + ": " + str(msg)
        plain_msg = "WARNING: " + str(msg)
        self.write_line(fancy_msg, v, plain_msg = plain_msg, agent = agent)

    def error(self, msg, v = -1, agent = None, err = ValueError):
        fancy_msg = color.BRIGHT_RED + color.BOLD + "ERROR" + color.END + ": " + color.bg.RED + str(msg) + color.bg.DEFAULT
        plain_msg = "ERROR: " + str(msg)
        self.write_line(fancy_msg, v, plain_msg = plain_msg, agent = agent)
        # Unless otherwise specified, we raise an exception of the proper type
        if err is not None:
            raise err(str(msg))

    def print_itemize(self, std_object, w = None, n = 6, min_w = None, v = -1, agent = None):
        # std_object is an object with the following properties:
        #   1. It is either a string, tuple, list, or dictionary
        #   2. Every nested element is a valid std_object
        # The strings act as leaves. The three iterables act as the following:
        #   1. Tuples represent itemized lists
        #   2. Lists represent numbered lists
        #   3. Dictionaries represent labelled lists.

        # If agent needs to be printed, we print it on the top
        agent_pre, agent_plain_pre = self.get_agent_tag(agent)
        if agent_plain_pre:
            self.write_line("", v = v, agent = agent, temporary_elements = False)

        w = self.max_allowed_w(w)
        if min_w is None:
            min_w = len(Journal.asterism)

        # We store all the lines in a list and then print it in a batch.
        fancy_print_queue = []
        plain_print_queue = []

        def commit_msg(itemize_depth, key, msg = None):
            nonlocal fancy_print_queue
            nonlocal plain_print_queue
            # We assume key is None for itemize, str for labelled, int for numbered
            if key is None:
                # Itemized
                plain_keystr = '-'
                prefix_len = (2 * itemize_depth) + 1
                fancy_keystr = color.fg_highlight('yellow', '-', True)
            elif isinstance(key, int):
                # Numbered
                plain_keystr = str(key) + '. '
                prefix_len = (2 * itemize_depth) + len(plain_keystr)
                fancy_keystr = color.fg_highlight('yellow', str(key) + '.', True) + ' '
            elif isinstance(key, str):
                # Labelled
                plain_keystr = key + ': '
                prefix_len = (2 * itemize_depth) + len(plain_keystr)
                fancy_keystr = color.fg_highlight('yellow', key + ':', True) + ' '
            if w < (2 * itemize_depth) + len(plain_keystr.rstrip()):
                # We skip the printing with an ellipsis
                fancy_print_queue.append(PMU_funcs.st('...', w))
                plain_print_queue.append(PMU_funcs.st('...', w))
                return
            if msg is None:
                fancy_print_queue.append(' ' * (2 * itemize_depth) + fancy_keystr.rstrip())
                plain_print_queue.append(' ' * (2 * itemize_depth) + plain_keystr.rstrip())
                return
            else:
                if w < prefix_len + min(min_w, len(msg)):
                    fancy_print_queue.append(PMU_funcs.st('...', w))
                    plain_print_queue.append(PMU_funcs.st('...', w))
                    return
                else:
                    sequenced_msg = PMU_funcs.wrap_text(msg, w - prefix_len, hyphenate = True, n = n)
                    fancy_print_queue.append(' ' * (2 * itemize_depth) + fancy_keystr + sequenced_msg[0])
                    plain_print_queue.append(' ' * (2 * itemize_depth) + plain_keystr + sequenced_msg[0])
                    for i in range(1, len(sequenced_msg)):
                        fancy_print_queue.append(' ' * prefix_len + sequenced_msg[i])
                        plain_print_queue.append(' ' * prefix_len + sequenced_msg[i])


        def peel_layer(cur_std_object, key = None, itemize_depth = 0):
            if isinstance(cur_std_object, str):
                # leaf
                commit_msg(itemize_depth, key, cur_std_object)
            else:
                # We print the key on its own
                if itemize_depth > 0:
                    commit_msg(itemize_depth, key)

                if isinstance(cur_std_object, dict):
                    # Labelled list
                    for label, value in cur_std_object.items():
                        peel_layer(value, str(label), itemize_depth + 1)
                elif isinstance(cur_std_object, tuple):
                    # Itemized list
                    for i in range(len(cur_std_object)):
                        peel_layer(cur_std_object[i], None, itemize_depth + 1)
                elif isinstance(cur_std_object, list):
                    # Numbered list
                    for i in range(len(cur_std_object)):
                        peel_layer(cur_std_object[i], i + 1, itemize_depth + 1)

        peel_layer(std_object)
        self.print_precomputed_batch(fancy_print_queue, plain_print_queue, v = v, agent = agent)

    def print_matrix(self, m, label, dec_points = 5, max_rows = 11, v = -1, agent = None):

        # First, we create the label prefix
        fancy_print_queue = []
        plain_print_queue = []
        def pq_app(msg, i, plain_msg = None):
            if plain_msg is None:
                plain_msg = msg
            fancy_print_queue[i] += msg
            plain_print_queue[i] += plain_msg
        no_of_rows = min(len(m), max_rows)

        def rdec(n):
            if isinstance(n, int):
                return(f"{n}")
            if isinstance(n, complex):
                if n.imag < 0:
                    return(f"{round(n.real, dec_points)}{round(n.imag, dec_points)}j")
                else:
                    return(f"{round(n.real, dec_points)}+{round(n.imag, dec_points)}j")
            return(f"{round(n, dec_points)}")

        fancy_pre_col = []
        plain_pre_col = []
        if no_of_rows == 1:
            fancy_pre_col = [color.fg_highlight('yellow', '(', True)]
            plain_pre_col = ["("]
        else:
            # fancy
            fancy_pre_col = [color.fg_highlight('yellow', '/', True)]
            for i in range(no_of_rows - 2):
                fancy_pre_col.append(color.fg_highlight('yellow', '|', True))
            fancy_pre_col.append(color.fg_highlight('yellow', '\\', True))
            # plain
            plain_pre_col = ["/"]
            for i in range(no_of_rows - 2):
                plain_pre_col.append("|")
            plain_pre_col.append("\\")

        for i in range(no_of_rows):
            if i == no_of_rows // 2:
                fancy_print_queue.append(f"{label} = {fancy_pre_col[i]}")
                plain_print_queue.append(f"{label} = {plain_pre_col[i]}")
            else:
                fancy_print_queue.append(" " * (len(label) + 3) + f"{fancy_pre_col[i]}")
                plain_print_queue.append(" " * (len(label) + 3) + f"{plain_pre_col[i]}")


        # Now, we calculate how many numbers we can afford to print to respect the line length
        col_width = [0] * len(m[0])
        for i in range(len(m)):
            for j in range(len(m[0])):
                cur_len = len(rdec(m[i][j])) + 2 # the 2 is for minimal padding
                if cur_len > col_width[j]:
                    col_width[j] = cur_len

        do_rows_need_trimming = sum(col_width) > (self.max_row_width - len(Journal.pipe) * self.depth - len(label) - 3)
        if do_rows_need_trimming:
            trim_N = 0 # number of entries we can display
            row_leeway = self.max_row_width - len(Journal.pipe) * self.depth - len(label) - 6 - col_width[-1]
            while(sum(col_width[:trim_N]) <= row_leeway and trim_N < len(m[0]) - 1):
                trim_N += 1
            trim_N = max(0, trim_N - 1)

        if not do_rows_need_trimming:
            # We can print the entire row
            if len(m) <= max_rows:
                # we can print the entire matrix
                for i in range(len(m)):
                    for j in range(len(m[i]) - 1):
                        pq_app(PMU_funcs.st(rdec(m[i][j]), col_width[j]), i)
                    pq_app(" " + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2), i)
            else:
                # we trim after max_rows - 2
                for i in range(max_rows - 2):
                    for j in range(len(m[i]) - 1):
                        pq_app(PMU_funcs.st(rdec(m[i][j]), col_width[j]), i)
                    pq_app(" " + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2), i)
                for j in range(len(m[0]) - 1):
                    pq_app(color.fg_highlight('yellow', PMU_funcs.st("...", col_width[j]), True), max_rows - 2, PMU_funcs.st("...", col_width[j]))
                pq_app(" " + color.fg_highlight('yellow', PMU_funcs.st("...", col_width[-1] - 2), True), max_rows - 2, " " + PMU_funcs.st("...", col_width[-1] - 2))
                for j in range(len(m[-1]) - 1):
                    pq_app(PMU_funcs.st(rdec(m[-1][j]), col_width[j]), max_rows - 1)
                pq_app(" " + PMU_funcs.st(rdec(m[-1][len(m[-1]) - 1]), col_width[-1] - 2), max_rows - 1)
        else:
            # we have to trim the number of entries per row
            if len(m) <= max_rows:
                # we can print all rows
                for i in range(len(m)):
                    for j in range(trim_N):
                        pq_app(PMU_funcs.st(rdec(m[i][j]), col_width[j]), i)
                    pq_app(color.fg_highlight('yellow', "... ", True) + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2), i, "... " + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2))
            else:
                # we trim rows and columns
                for i in range(max_rows - 2):
                    for j in range(trim_N):
                        pq_app(PMU_funcs.st(rdec(m[i][j]), col_width[j]), i)
                    pq_app(color.fg_highlight('yellow', "... ", True) + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2), i, "... " + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2))
                for j in range(trim_N):
                    pq_app(color.fg_highlight('yellow', PMU_funcs.st("...", col_width[j]), True), max_rows - 2, PMU_funcs.st("...", col_width[j]))
                pq_app("    " + color.fg_highlight('yellow', PMU_funcs.st("...", col_width[-1] - 2), True), max_rows - 2, "    " + PMU_funcs.st("...", col_width[-1] - 2))
                for j in range(trim_N):
                    pq_app(PMU_funcs.st(rdec(m[-1][j]), col_width[j]), max_rows - 1)
                pq_app(color.fg_highlight('yellow', "... ", True) + PMU_funcs.st(rdec(m[-1][len(m[-1]) - 1]), col_width[-1] - 2), max_rows - 1, "... " + PMU_funcs.st(rdec(m[-1][len(m[-1]) - 1]), col_width[-1] - 2))

        self.print_precomputed_batch(fancy_print_queue, plain_print_queue, v = v, agent = agent)



    def print_table(self, table_name, column_names, row_names, list_of_rows, subtable_borders = None, w = None, align = None, hline = None, header_separation = 2, v = -1, agent = None):
        # column_names[N], row_names[M], list_of_rows[M][N]
        # subtable_borders is a list of column indices which have a horizontal
        # separator on their right side.
        # w[N + 1] is the maximal allowed width for each column, starting with
        # the row name column.
        # align[N] is the align mode for each column. These can be:
        #   -None: completely automatic
        #   -single char:
        #      -'t' = (automatic, top)
        #      -'b' = (automatic, bottom)
        #      -'l' = (left, automatic)
        #      -'r' = (right, automatic)
        #      -'c' = (center, center)
        #   -two-char string or tuple of single chars; these specify the
        #    horizontal and vertical alignment, respectively
        # hline manages the way rows are separated from each other. It consists
        # of two characters, or is brought to that form using autofill.
        #   -First character specifies the form hline takes:
        #      -'u' [default]: All cells are underlined.
        #      -'s': Empty space between all cells
        #   -Second character specifies to which cells and under what condition
        #    does the hline apply:
        #      -'a' [default]: All cells affected if at least one's height > 1.
        #      -'f': All cells always affected.
        #      -'c': Only cells of height > 1 affected.
        #      -'n': Hline is never applied.

        default_hline = "ua"
        hline_options = [['u', 's'], ['a', 'f', 'c', 'n']]

        # We normalise function arguments
        if subtable_borders is None:
            subtable_borders = []
        if w is None:
            w = [None] * (len(column_names) + 1)
        if align is None:
            align = [None] * len(column_names)
        if not isinstance(align, list):
            align = [align] * len(column_names)

        # Input validation
        if len(w) != len(column_names) + 1:
            self.error(f"Incorrect length of minimum-width list: {len(w)} given, {len(column_names) + 1} (No. of cols + 1) expected.")

        if len(align) != len(column_names):
            self.error(f"Incorrect length of alignment specification list: {len(align)} given, {len(column_names)} (No. of cols) expected.")

        if len(row_names) != len(list_of_rows):
            self.error(f"Row number mismatch: {len(list_of_rows)} rows given, {len(row_names)} row labels given.")

        if any(len(row) != len(column_names) for row in list_of_rows):
            self.error("Incorrect number of cells in a data row.")

        sequenced_cells = [] # [M][N] = [line1, line2, ...]
        sequenced_column_names = [] # [N] = [line1, line2, ...]
        sequenced_row_names = [] # [M] = [line1, line2, ...]
        sequenced_table_name = None
        header_height = 0
        row_heights = [0] * len(row_names)

        # here we normalise hline
        if isinstance(hline, (str, list, tuple)):
            if len(hline) == 1:
                if hline[0] in hline_options[0]:
                    hline = hline[0] + default_hline[1]
                elif hline[0] in hline_options[1]:
                    hline = default_hline[0] + hline[0]
                else:
                    hline = default_hline
            elif len(hline) == 2:
                if hline[0] not in hline_options[0]:
                    hline = default_hline[0] + hline[1]
                if hline[1] not in hline_options[1]:
                    hline = hline[0] + default_hline[1]
            else:
                hline = default_hline
        else:
            hline = default_hline


        fancy_print_queue = [] # each line is an element
        plain_print_queue = []

        if self.fancy_printing:
            fancy_vert_sep = color.fg_highlight('yellow', '|', True)
        plain_vert_sep = "|"
        vert_sep_len = len(plain_vert_sep)

        max_len_row_names = len(str(table_name))
        for row_name in row_names:
            if len(str(row_name)) > max_len_row_names:
                max_len_row_names = len(str(row_name))
        max_len_row_names = PMU_funcs.min_with_none(max_len_row_names, w[0])
        max_len_by_column = []
        for j in range(len(column_names)):
            max_len_by_column.append(len(str(column_names[j])))
            for i in range(len(row_names)):
                if max_len_by_column[j] < len(str(list_of_rows[i][j])):
                    max_len_by_column[j] = len(str(list_of_rows[i][j]))
            max_len_by_column[j] = PMU_funcs.min_with_none(max_len_by_column[j], w[j + 1])

        # We now convert each cell to a list of lines to take care of wrapping the text

        # First, we wrap_and_halign everything to calculate the minimal required heights per row

        sequenced_table_name = PMU_funcs.wrap_and_halign(table_name, max_len_row_names, align = "c", n = max_len_row_names)
        header_height = len(sequenced_table_name)

        for i in range(len(row_names)):
            sequenced_row_names.append(PMU_funcs.wrap_and_halign(row_names[i], max_len_row_names, align = "rt", n = max_len_row_names))
            row_heights[i] = len(sequenced_row_names[i])

        for i in range(len(row_names)):
            sequenced_cells.append([])
        for j in range(len(column_names)):
            sequenced_column_names.append(PMU_funcs.wrap_and_halign(column_names[j], max_len_by_column[j], align = 'cb'))
            if header_height < len(sequenced_column_names[j]):
                header_height = len(sequenced_column_names[j])

            for i in range(len(row_names)):
                sequenced_cells[i].append(PMU_funcs.wrap_and_halign(list_of_rows[i][j], max_len_by_column[j], align = align[j]))
                if row_heights[i] < len(sequenced_cells[i][j]):
                    row_heights[i] = len(sequenced_cells[i][j])

        # Now we apply valign to all cells to normalise heights

        sequenced_table_name = PMU_funcs.valign(sequenced_table_name, header_height, align = 'c')

        for i in range(len(row_names)):
            sequenced_row_names[i] = PMU_funcs.valign(sequenced_row_names[i], row_heights[i], align = 't')

        for j in range(len(column_names)):
            cur_valign = PMU_funcs.standard_align(None, align[j])[1]
            sequenced_column_names[j] = PMU_funcs.valign(sequenced_column_names[j], header_height, align = "b")
            for i in range(len(row_names)):
                sequenced_cells[i][j] = PMU_funcs.valign(sequenced_cells[i][j], row_heights[i], align = cur_valign)

        # We initialise the per-row hline instruction
        if hline[1] == 'n':
            hline_per_row = [False] * len(row_names)
        elif hline[1] == 'f':
            hline_per_row = [True] * len(row_names)
        elif hline[1] == 'a':
            hline_per_row = [False] * len(row_names)
            for i in range(len(row_names)):
                if row_heights[i] > 1:
                    hline_per_row = [True] * len(row_names)
                    break
        elif hline[1] == 'c':
            hline_per_row = [False] * len(row_names)
            for i in range(len(row_names)):
                if row_heights[i] > 1:
                    hline_per_row[i] = True

        if hline[0] == 's':
            # We insert an empty line to every hline-positive cell
            for i in range(len(row_names) - 1):
                if not hline_per_row[i]:
                    continue
                sequenced_row_names[i].append(' ' * max_len_row_names)
                for j in range(len(column_names)):
                    sequenced_cells[i][j].append(' ' * max_len_by_column[j])
                row_heights[i] += 1


        # We calculate header_length, the plaintext width of the table
        header_length = max_len_row_names + header_separation + vert_sep_len

        # We now queue in the header row
        for i in range(len(column_names)):
            header_length += max_len_by_column[i] + header_separation
            if i in subtable_borders:
                header_length += vert_sep_len

        for k in range(header_height):

            if self.fancy_printing:
                fancy_header_str = PMU_funcs.st(sequenced_table_name[k], max_len_row_names + header_separation) + fancy_vert_sep
                for i in range(len(column_names)):
                    fancy_header_str += PMU_funcs.st(sequenced_column_names[i][k], max_len_by_column[i] + header_separation)
                    if i in subtable_borders:
                        fancy_header_str += fancy_vert_sep
                fancy_print_queue.append(fancy_header_str)

            plain_header_str = PMU_funcs.st(sequenced_table_name[k], max_len_row_names + header_separation) + plain_vert_sep
            for i in range(len(column_names)):
                plain_header_str += PMU_funcs.st(sequenced_column_names[i][k], max_len_by_column[i] + header_separation)
                if i in subtable_borders:
                    plain_header_str += plain_vert_sep
            plain_print_queue.append(plain_header_str)


        if self.fancy_printing:
            fancy_print_queue.append(color.fg_highlight('yellow', "-" * header_length, True))
        plain_print_queue.append("-" * header_length)
        for i in range(len(row_names)):

            for k in range(row_heights[i]):

                if self.fancy_printing:
                    row_name_line = PMU_funcs.st(sequenced_row_names[i][k], max_len_row_names + header_separation)
                    if hline[0] == 'u' and hline_per_row[i] and k == row_heights[i] - 1 and i != len(row_names) - 1:
                        row_name_line = color.underline(row_name_line)
                    fancy_cur_str = row_name_line + fancy_vert_sep
                    for j in range(len(column_names)):
                        cell_line = PMU_funcs.st(sequenced_cells[i][j][k], max_len_by_column[j] + header_separation)
                        if hline[0] == 'u' and hline_per_row[i] and k == row_heights[i] - 1 and i != len(row_names) - 1:
                            cell_line = color.underline(cell_line)
                        fancy_cur_str += cell_line
                        if j in subtable_borders:
                            fancy_cur_str += fancy_vert_sep
                    fancy_print_queue.append(fancy_cur_str)
                plain_cur_str = PMU_funcs.st(sequenced_row_names[i][k], max_len_row_names + header_separation) + plain_vert_sep
                for j in range(len(column_names)):
                    plain_cur_str += PMU_funcs.st(sequenced_cells[i][j][k], max_len_by_column[j] + header_separation)
                    if j in subtable_borders:
                        plain_cur_str += plain_vert_sep
                plain_print_queue.append(plain_cur_str)
        if self.fancy_printing:
            fancy_print_queue.append(color.fg_highlight('yellow', "-" * header_length, True))
        plain_print_queue.append("-" * header_length)

        self.print_precomputed_batch(fancy_print_queue, plain_print_queue, v = v, agent = agent)

    """
    def print_paragraph(self, msg, w = None, v = -1, agent = None, n = 6, min_w = None):
        # msg must be plain text
        if min_w is None:
            min_w = len(Journal.asterism)
        wrapped_msg = PMU_funcs.wrap_text(msg, w = self.max_allowed_w(w), min_w = min_w)

        for line in wrapped_msg:
            self.write(line, v = v, agent = agent)"""


    def print_dinkus(self, w = None, v = -1, agent = None):
        w = self.max_allowed_w(w)
        if w < len(Journal.asterism):
            # Cannot print anything
            return
        self.write_line(PMU_funcs.st(color.fg_highlight('yellow', Journal.asterism, True), w, '-', plain_len = len(Journal.asterism)), v = v, plain_msg = PMU_funcs.st(Journal.asterism, w, '-'), agent = agent)

    # Routine stack management

    def enter(self, header, v = -1, semaphored = False, agent = None, **kwargs):
        # header: human-readable name of routine
        # v: verbosity requirement

        # semaphored: if True, the routine is semaphored
        # if semaphored, the following kwargs are needed:
        #   -label [str]: Short identification of the process
        #   -tau_space [number or tuple]: specifies tau_max and, if provided, number of divisions.
        #   -update_on_every_tick [bool] (default False): If True, every process update flushes the output. If False, only changes in divisions flush the output.
        #   -c [str] (default 'green'): keyword for the progress bar color.
        #   -width [int] (default 20): width of the progress bar.


        new_ID = None
        header_fancy = header
        if semaphored:
            # We register the new event
            new_ID = self.semaphor.create_event(**kwargs)
            header_fancy = self.semaphor.fg_highlight(new_ID, header)

        self.routine_stack.append([header, max(v, self.get_stack_v()), agent, new_ID])

        self.write_line(header_fancy, v, agent = agent, plain_msg = header)
        self.depth += 1

        self.update_stack_agent()

        if semaphored:
            return new_ID

    # ------------------------ Semaphor update methods ------------------------

    def get_standard_S_ID(self, S_ID):
        if S_ID is None:
            # If there is only one semaphor event, this is fine. Otherwise, this is an error.
            if len(self.semaphor.processes) == 1:
                return list(self.semaphor.processes.keys())[0]
            else:
                self.error("Semaphor process ID must be provided on update if more than one process exists.")
        return S_ID

    def semaphor_update(self, tau, S_ID = None):
        if self.semaphor.update(self.get_standard_S_ID(S_ID), tau):
            # We updated. Time to flush the highlight
            self.reload_preview()

    def semaphor_progress(self, tau_progress = 1, S_ID = None):
        if self.semaphor.progress(self.get_standard_S_ID(S_ID), tau_progress):
            # We updated. Time to flush the highlight
            self.reload_preview()

    def semaphor_overtime(self, tau_overtime = 1, S_ID = None):
        if self.semaphor.overtime(self.get_standard_S_ID(S_ID), tau_overtime):
            # We updated. Time to flush the highlight
            self.reload_preview()


    def exit(self, end_message = None):
        # If popping a semaphor, it will return the duration in ms
        last_routine = self.routine_stack.pop()


        if end_message is not None:
            exit_msg_plain = end_message
        else:
            exit_msg_plain = ""
        exit_msg_fancy = exit_msg_plain

        # check if it's semaphored
        was_it_semaphored = last_routine[3] is not None
        if was_it_semaphored:
            # We exit the semaphored routine, This overrides the exit msg.
            process_duration, exit_msg_fancy, exit_msg_plain = self.semaphor.finish_event(last_routine[3])
            self.cur_semaphor_event = None
            self.cur_semaphor_prefix_id = 0
        self.depth -= 1
        self.write_line(exit_msg_fancy, last_routine[1], plain_msg = exit_msg_plain, is_exit = True)
        self.update_stack_agent()
        if was_it_semaphored:
            return process_duration

    # Interactive element

    def ask_yes_no(self, question, agent = None):
        # Requires a print on the fly method.
        # Doesn't proceed until given answer
        # Returns True if yes, False if no

        if self.yes is not None:
            if self.yes:
                self.write_line(question + " (Automatically decided '" + color.fg_highlight('green', 'yes', False) + "')", plain_msg = question + " (Automatically decided 'yes')", agent = agent)
            else:
                self.write_line(question + " (Automatically decided '" + color.fg_highlight('red', 'no', False) + "')", plain_msg = question + " (Automatically decided 'no')", agent = agent)
            return(self.yes)

        if not self.print_on_the_fly:
            # Assume yes
            self.write_line(question + " (Assumed '" + color.fg_highlight('green', 'yes', False) + "')", plain_msg = question + " (Assumed 'yes')", agent = agent)
            return(True)

        # First, we commit the previous line
        self.commit_last_line()

        ans = "NOT_PROVIDED"

        agent_pre, agent_plain_pre = self.get_agent_tag(agent)

        question_print = self.pre() + agent_plain_pre + question + " (y / n) "
        if self.fancy_printing:
            question_print = self.pre() + agent_pre + color.bold(question) + " (" + color.fg_highlight('green', 'y', False) + " / " + color.fg_highlight('red', 'n', False) + ") "

        while ans not in Journal.valid_answers:
            ans = input(question_print).strip().lower()

        if ans in Journal.answer_strings["yes"]:
            self.write_line(question + " (Answered 'yes')", prevent_printing_on_the_fly = True)
            return(True)
        if ans in Journal.answer_strings["no"]:
            self.write(question + " (Answered 'no')", prevent_printing_on_the_fly = True)
            return(False)

    # -------------- Agent tag management -------------------

    def register_agent_tag(self, ID, tag):
        # color is in the form ("keyword", is bright?)
        if "color" not in tag:
            tag["color"] = None
        elif isinstance(tag["color"], str):
            # We add the brightness option as a default value of False
            tag["color"] = (tag["color"], False)

        self.agent_tags[ID] = tag

    def get_agent_tag(self, ID):
        if ID is None or ID == self.stack_agent:
            return("", "")
        elif ID not in self.agent_tags:
            return("", "")
        elif self.agent_tags[ID]["color"] is None:
            return ("[" + self.agent_tags[ID]["label"] + "] ", "[" + self.agent_tags[ID]["label"] + "] ")
        elif isinstance(self.agent_tags[ID]["color"], str):
            return ("[" + color.fg_highlight(self.agent_tags[ID]["color"], self.agent_tags[ID]["label"], bright = False) + "] ", "[" + self.agent_tags[ID]["label"] + "] ")
        else:
            return ("[" + color.fg_highlight(self.agent_tags[ID]["color"][0], self.agent_tags[ID]["label"], bright = self.agent_tags[ID]["color"][1]) + "] ", "[" + self.agent_tags[ID]["label"] + "] ")

# -----------------------------------------------------------------------------
# ---------------------------- Singleton instance -----------------------------
# -----------------------------------------------------------------------------

journal = Journal()
