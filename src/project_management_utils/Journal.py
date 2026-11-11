from . import PMU_funcs

from .color import color
from .Printable_Semaphor import Printable_Semaphor

# -----------------------------------------------------------------------------
# -------------------------- Typographical constants --------------------------
# -----------------------------------------------------------------------------

# -------------------------------- Delimiters ---------------------------------
nested_semaphor_delim = " | "

# ---------------------------------- Colors -----------------------------------


gradual_fg_color = [ # used for pipes. Highlights routine depth. Cycles.
    color.BRIGHT_BLUE,
    color.BRIGHT_MAGENTA,
    color.CYAN,
    color.BRIGHT_CYAN
    ]

# -----------------------------------------------------------------------------
# ------------------------------- class Journal -------------------------------
# -----------------------------------------------------------------------------

class Journal():

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
        sample_journal.error("This is a sample error.")

        sample_journal.enter("Testing item list printing...")
        sample_journal.print_itemize({
            "print_itemize" : "Prints an itemized/enumerated list from a standard object. Supports nested lists.",
            "nested numbered list" : ["First element", "Second element", {"this" : "First part of third element", "that" : "Second part of third element"}, "Fourth element"],
            "nested itemized list" : {"Keyword" : "Value", "Other keyword" : "Other value"}
            })
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
            row_names = ["verbosity", "print_on_the_fly", "fancy_printing", "max_row_width", "yes", "plain_semaphor_N"],
            list_of_rows = [
                [sample_journal.verbosity, 5, "Only logs with lower or equal value of verbosity are printed."],
                [sample_journal.print_on_the_fly, "True", "Whether the log is also printed to an output stream."],
                [sample_journal.fancy_printing, "True", "Formatting: font weight and color, rolling last line."],
                [sample_journal.max_row_width, 200, "Rows get trimmed if length exceeds this value."],
                [sample_journal.yes, None, "If not None, used instead of asking for input."],
                [sample_journal.plain_semaphor_N, 20, "Forced number of flags for a plain semaphor event."]
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
        self.verbosity = verbosity # The higher the verbosity, the more in detail the Journal is
        self.print_on_the_fly = print_on_the_fly # If True, printing to terminal happens concurrently
        self.depth = 0

        self.plain_semaphor_N = 20 # forced number of flags for a plain semaphor event

        self.fancy_printing = fancy_printing # if True, we use colors, highlighting etc

        self.max_row_width = max_row_width # used for clever wrapping

        self.yes = yes # If not None, used instead of asking for input

        self.last_printed_line = None # Always printed with \r until next line is staged, with different colour
        self.last_printed_depth = 0

        self.semaphor = Printable_Semaphor() # The in-house semaphor used to hang on a routine
        self.cur_semaphor_event = None
        self.cur_semaphor_prefix_id = 0

        self.agent_tags = {} # Used to distinguish write sources. Each tag has the form "agent" : {"label" : "agent name", "color" : "color code"}

    def close_journal(self):
        if self.print_on_the_fly:
            if self.fancy_printing:
                self.commit_last_line()
            print("-" * 30 + " Process finished " + "-" * 30)

    def dump(self):
        # dumps journal into string
        return(self.journal_text)

    # --------------------------- Prefix management ---------------------------

    def pipe_stack(self, n, allow_fancy = True):
        if self.fancy_printing and allow_fancy:
            res = ""
            for i in range(n):
                res += gradual_fg_color[i % len(gradual_fg_color)] + "|" + color.END + " "
            return(res)
        else:
            return("| " * n)

    def pre(self, allow_fancy = True, add_progress_bar = False, enforce_depth = None):
        # prefix for current depth.

        if enforce_depth is None:
            enforce_depth = self.depth

        # The general form is [pipes] [progress bars (in highlight only)]
        res = self.pipe_stack(enforce_depth, allow_fancy)
        if len(self.semaphor.processes) > 0 and add_progress_bar:
            res += self.semaphor.progress_bars(self.fancy_printing and allow_fancy) + " "
        return(res)

    def get_stack_v(self):
        # If stack is non-empty, we return last max req verbosity from stack; -1 otherwise (no requirement)
        if len(self.routine_stack) > 0:
            return(self.routine_stack[-1][1])
        return(-1)

    def get_stack_agent(self):
        if len(self.routine_stack) > 0:
            return(self.routine_stack[-1][2])
        return(None)

    # fancy printing methods

    def cur_highlight(self, raw):
        return(color.BOLD + raw + color.LIGHT)

    def commit_last_line(self, padding_length = 0):
        if self.last_printed_line is not None:
            print(self.pipe_stack(self.last_printed_depth) + self.last_printed_line + ' ' * padding_length)
            self.last_printed_line = None

    def preview_print(self, msg, update_last_printed_depth = True):
        # If fancy printing is enabled, we always pre-print the last line in bold
        if update_last_printed_depth:
            self.last_printed_depth = self.depth
        self.last_printed_line = msg
        print(self.pre(add_progress_bar = True, enforce_depth = self.last_printed_depth) + self.cur_highlight(msg), end="\r")

    def reload_preview(self):
        if self.print_on_the_fly and self.fancy_printing:
            self.preview_print(self.last_printed_line, update_last_printed_depth = False)

    # Write method

    def write(self, msg, v = -1, prevent_printing_on_the_fly = False, plain_msg = None, agent = None, padding_length = None):
        # Writes a message inside current routine at current depth

        # Only input padding_length manually when the length needs to be reserved before altering the semaphor status (like on finishing semaphor events)
        if padding_length is None:
            padding_length = self.semaphor.padding_length

        agent_pre, agent_plain_pre = self.get_agent_tag(agent)

        if self.verbosity >= max(v, self.get_stack_v()):
            if plain_msg is None:
                plain_msg = msg

            self.journal_text += self.pre(False) + agent_plain_pre + plain_msg + "\n"
            if self.print_on_the_fly and not prevent_printing_on_the_fly:
                if self.fancy_printing:
                    # We firstly print the last submitted line, and then the preprint of the current line
                    self.commit_last_line(padding_length)
                    self.preview_print(agent_pre + msg)
                else:
                    # crude printing only
                    print(self.pre() + agent_plain_pre + msg)

    # Special object printing methods

    def warning(self, msg, v = -1, agent = None):
        fancy_msg = color.BRIGHT_YELLOW + color.BOLD + "WARNING" + color.END + ": " + str(msg)
        plain_msg = "WARNING: " + str(msg)
        self.write(fancy_msg, v, plain_msg = plain_msg, agent = agent)

    def error(self, msg, v = -1, agent = None):
        fancy_msg = color.BRIGHT_RED + color.BOLD + "ERROR" + color.END + ": " + color.bg.RED + str(msg) + color.bg.DEFAULT
        plain_msg = "ERROR: " + str(msg)
        self.write(fancy_msg, v, plain_msg = plain_msg, agent = agent)

    def print_itemize(self, std_object, agent = None):
        # std_object is an object with the following properties:
        #   1. It is either a dict or a list
        #   2. Every element is either a valid std_object or a string
        def peel_layer(cur_std_object, key = None, itemize_depth = 0):
            if isinstance(cur_std_object, dict):
                if key is not None:
                    plain_msg = " " * (2 * itemize_depth) + "-" + str(key)
                    if self.fancy_printing:
                        self.write(" " * (2 * itemize_depth) + color.BRIGHT_YELLOW + "-" + color.END + str(key), plain_msg = plain_msg, agent = agent)
                    else:
                        self.write(plain_msg, agent = agent)
                for label, value in cur_std_object.items():
                    peel_layer(value, label, itemize_depth + 1)
            elif isinstance(cur_std_object, list):
                if key is not None:
                    plain_msg = " " * (2 * itemize_depth) + "-" + str(key)
                    if self.fancy_printing:
                        self.write(" " * (2 * itemize_depth) + color.BRIGHT_YELLOW + "-" + color.END + str(key), plain_msg = plain_msg, agent = agent)
                    else:
                        self.write(plain_msg, agent = agent)
                for i in range(len(cur_std_object)):
                    peel_layer(cur_std_object[i], str(i + 1), itemize_depth + 1)
            else:
                plain_msg = " " * (2 * itemize_depth) + f"-{key}: {cur_std_object}"
                if self.fancy_printing:
                    self.write(" " * (2 * itemize_depth) + color.BRIGHT_YELLOW + "-" + color.END + f"{key}: {cur_std_object}", plain_msg = plain_msg, agent = agent)
                else:
                    self.write(plain_msg, agent = agent)

        peel_layer(std_object)

    def print_matrix(self, m, label, dec_points = 5, max_rows = 11):

        # First, we create the label prefix
        fancy_print_queue = []
        plain_print_queue = []
        def pq_app(msg, i):
            if self.fancy_printing:
                fancy_print_queue[i] += msg
            plain_print_queue[i] += msg
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
            if self.fancy_printing:
                fancy_pre_col = [color.BRIGHT_YELLOW + "(" + color.END]
            plain_pre_col = ["("]
        else:
            if self.fancy_printing:
                fancy_pre_col = [color.BRIGHT_YELLOW + "/" + color.END]
                for i in range(no_of_rows - 2):
                    fancy_pre_col.append(color.BRIGHT_YELLOW + "|" + color.END)
                fancy_pre_col.append(color.BRIGHT_YELLOW + "\\" + color.END)
            plain_pre_col = ["/"]
            for i in range(no_of_rows - 2):
                plain_pre_col.append("|")
            plain_pre_col.append("\\")

        for i in range(no_of_rows):
            if i == no_of_rows // 2:
                if self.fancy_printing:
                    fancy_print_queue.append(f"{label} = {fancy_pre_col[i]}")
                plain_print_queue.append(f"{label} = {plain_pre_col[i]}")
            else:
                if self.fancy_printing:
                    fancy_print_queue.append(" " * (len(label) + 3) + f"{fancy_pre_col[i]}")
                plain_print_queue.append(" " * (len(label) + 3) + f"{plain_pre_col[i]}")


        # Now, we calculate how many numbers we can afford to print to respect the line length
        col_width = [0] * len(m[0])
        for i in range(len(m)):
            for j in range(len(m[0])):
                cur_len = len(rdec(m[i][j])) + 2 # the 2 is for minimal padding
                if cur_len > col_width[j]:
                    col_width[j] = cur_len

        do_rows_need_trimming = sum(col_width) > (self.max_row_width - 2 * self.depth - len(label) - 3)
        if do_rows_need_trimming:
            trim_N = 0 # number of entries we can display
            row_leeway = self.max_row_width - 2 * self.depth - len(label) - 6 - col_width[-1]
            while(sum(col_width[:trim_N]) <= row_leeway and trim_N < len(m) - 1):
                trim_N += 1
            trim_N -= 1

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
                    pq_app(PMU_funcs.st("...", col_width[j]), max_rows - 2)
                pq_app(" " + PMU_funcs.st("...", col_width[-1] - 2), max_rows - 2)
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
                    pq_app("... " + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2), i)
            else:
                # we trim rows and columns
                for i in range(max_rows - 2):
                    for j in range(trim_N):
                        pq_app(PMU_funcs.st(rdec(m[i][j]), col_width[j]), i)
                    pq_app("... " + PMU_funcs.st(rdec(m[i][len(m[i]) - 1]), col_width[-1] - 2), i)
                for j in range(trim_N):
                    pq_app(PMU_funcs.st("...", col_width[j]), max_rows - 2)
                pq_app("    " + PMU_funcs.st("...", col_width[-1] - 2), max_rows - 2)
                for j in range(trim_N):
                    pq_app(PMU_funcs.st(rdec(m[-1][j]), col_width[j]), max_rows - 1)
                pq_app("... " + PMU_funcs.st(rdec(m[-1][len(m[-1]) - 1]), col_width[-1] - 2), max_rows - 1)

        for i in range(len(plain_print_queue)):
            if self.fancy_printing:
                self.write(fancy_print_queue[i], plain_msg = plain_print_queue[i])
            else:
                self.write(plain_print_queue[i])




    def print_table(self, table_name, column_names, row_names, list_of_rows, subtable_borders = [], header_separation = 2):
        # column_names[N], row_names[M], list_of_rows[M][N]

        fancy_print_queue = [] # each line is an element
        plain_print_queue = []

        if self.fancy_printing:
            fancy_vert_sep = color.BRIGHT_YELLOW + "|" + color.END
        plain_vert_sep = "|"
        vert_sep_len = len(plain_vert_sep)

        max_len_row_names = len(str(table_name))
        for row_name in row_names:
            if len(str(row_name)) > max_len_row_names:
                max_len_row_names = len(row_name)
        max_len_by_column = []
        for column_name in column_names:
            max_len_by_column.append(len(str(column_name)))

        for j in range(len(column_names)):
            for i in range(len(row_names)):
                if max_len_by_column[j] < len(str(list_of_rows[i][j])):
                    max_len_by_column[j] = len(str(list_of_rows[i][j]))

        if self.fancy_printing:
            fancy_header_str = PMU_funcs.st(table_name, max_len_row_names + header_separation) + fancy_vert_sep
            for i in range(len(column_names)):
                fancy_header_str += PMU_funcs.st(column_names[i], max_len_by_column[i] + header_separation)
                if i in subtable_borders:
                    fancy_header_str += fancy_vert_sep
        plain_header_str = PMU_funcs.st(table_name, max_len_row_names + header_separation) + plain_vert_sep
        header_length = max_len_row_names + header_separation + vert_sep_len
        for i in range(len(column_names)):
            plain_header_str += PMU_funcs.st(column_names[i], max_len_by_column[i] + header_separation)
            header_length += max_len_by_column[i] + header_separation
            if i in subtable_borders:
                plain_header_str += plain_vert_sep
                header_length += vert_sep_len

        if self.fancy_printing:
            fancy_print_queue.append(fancy_header_str)
        plain_print_queue.append(plain_header_str)
        if self.fancy_printing:
            fancy_print_queue.append(color.BRIGHT_YELLOW + "-" * header_length + color.END)
        plain_print_queue.append("-" * header_length)
        for i in range(len(row_names)):
            if self.fancy_printing:
                fancy_cur_str = PMU_funcs.st(row_names[i], max_len_row_names + header_separation) + fancy_vert_sep
                for j in range(len(column_names)):
                    fancy_cur_str += PMU_funcs.st(list_of_rows[i][j], max_len_by_column[j] + header_separation)
                    if j in subtable_borders:
                        fancy_cur_str += fancy_vert_sep
                fancy_print_queue.append(fancy_cur_str)
            plain_cur_str = PMU_funcs.st(row_names[i], max_len_row_names + header_separation) + plain_vert_sep
            for j in range(len(column_names)):
                plain_cur_str += PMU_funcs.st(list_of_rows[i][j], max_len_by_column[j] + header_separation)
                if j in subtable_borders:
                    plain_cur_str += plain_vert_sep
            plain_print_queue.append(plain_cur_str)
        if self.fancy_printing:
            fancy_print_queue.append(color.BRIGHT_YELLOW + "-" * header_length + color.END)
        plain_print_queue.append("-" * header_length)

        for i in range(len(plain_print_queue)):
            if self.fancy_printing:
                self.write(fancy_print_queue[i], plain_msg = plain_print_queue[i])
            else:
                self.write(plain_print_queue[i])



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
            header_fancy = self.semaphor.bg_highlight(new_ID, header)

        self.routine_stack.append([header, max(v, self.get_stack_v()), agent, new_ID])

        self.write(header_fancy, v, agent = agent, plain_msg = header)
        self.depth += 1

        if semaphored:
            return new_ID

    # ------------------------ Semaphor update methods ------------------------

    def get_standard_S_ID(self, S_ID):
        if S_ID is None:
            # If there is only one semaphor event, this is fine. Otherwise, this is an error.
            if len(self.semaphor.processes) == 1:
                return list(self.semaphor.processes.keys())[0]
            else:
                raise Exception("Semaphor process ID must be provided on update if more than one process exists.")
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
            exit_msg_plain = " " + end_message
        else:
            exit_msg_plain = ""
        exit_msg_fancy = exit_msg_plain

        padding_length = self.semaphor.padding_length

        # check if it's semaphored
        was_it_semaphored = last_routine[3] is not None
        if was_it_semaphored:
            # We exit the semaphored routine
            process_duration, semaphor_exit_msg_fancy, semaphor_exit_msg_plain = self.semaphor.finish_event(last_routine[3])
            self.cur_semaphor_event = None
            self.cur_semaphor_prefix_id = 0
            exit_msg_fancy = " " + semaphor_exit_msg_fancy
            exit_msg_plain = " " + semaphor_exit_msg_plain
        self.depth -= 1
        self.write(gradual_fg_color[self.depth % len(gradual_fg_color)] + "\\_" + color.END + exit_msg_fancy, last_routine[1], plain_msg = "\\_" + exit_msg_plain, padding_length = padding_length)
        if was_it_semaphored:
            return process_duration

    # Interactive element

    def ask_yes_no(self, question, agent = None):
        # Requires a print on the fly method.
        # Doesn't proceed until given answer
        # Returns True if yes, False if no

        if self.yes is not None:
            if self.yes:
                self.write(question + " (Automatically decided 'yes')", agent = agent)
            else:
                self.write(question + " (Automatically decided 'no')", agent = agent)
            return(self.yes)

        if not self.print_on_the_fly:
            # Assume yes
            self.write(question + " (Assumed 'yes')", agent = agent)
            return(True)

        # First, we commit the previous line
        self.commit_last_line()

        ans = "NOT_PROVIDED"

        agent_pre, agent_plain_pre = self.get_agent_tag(agent)

        question_print = self.pre() + agent_plain_pre + question + " (y / n) "
        if self.fancy_printing:
            question_print = self.pre() + agent_pre + self.cur_highlight(question) + " (" + color.GREEN + "y" + color.END + " / " + color.RED + "n" + color.END + ") "

        while ans.lower() not in Journal.valid_answers:
            ans = input(question_print)

        if ans in Journal.answer_strings["yes"]:
            self.write(question + "(Answered 'yes')", prevent_printing_on_the_fly = True)
            return(True)
        if ans in Journal.answer_strings["no"]:
            self.write(question + "(Answered 'no')", prevent_printing_on_the_fly = True)
            return(False)

    # -------------- Agent tag management -------------------

    def register_agent_tag(self, ID, tag):
        self.agent_tags[ID] = tag

    def get_agent_tag(self, ID):
        if ID is None or ID == self.get_stack_agent():
            return("", "")
        if ID not in self.agent_tags:
            return("", "")
        return("[" + self.agent_tags[ID]["color"] + self.agent_tags[ID]["label"] + color.END + "]" + " ", "[" + self.agent_tags[ID]["label"] + "] ")

# -----------------------------------------------------------------------------
# --------------------------- class DisabledJournal ---------------------------
# -----------------------------------------------------------------------------
# Pass this as a Journal to prevent printing without throwing exceptions on
# method calls

class DisabledJournal():
    def __init__(self, verbosity = 0, print_on_the_fly = True, fancy_printing = True, max_row_width = 200):
        pass

    def write(self, msg, v = -1, prevent_printing_on_the_fly = False):
        pass

    def enter(self, header, v = -1, semaphored = False, **kwargs):
        pass

    def exit(self, end_message = None):
        pass

    def print_matrix(self, m, label, dec_points = 5, max_rows = 11):
        pass

    def print_table(self, table_name, column_names, row_names, list_of_rows, subtable_borders = [], header_separation = 2):
        pass

    def update_semaphor_event(self, tau):
        pass

