
# First, we import the utilities
from utils.class_Disk_Jockey import Disk_Jockey
from utils.class_Journal import Journal
from utils.class_Semaphor import Semaphor

import numpy as np

class John_Physics:

    # solves physics

    def __init__(self, ID, log_verbosity = 5):

        self.ID = ID # A string that identifies this instance of John_Physics. It is the "experiment's label".

        # Firstly, we initialise an instance of Journal (for logging) and Disk Jockey (for data management)
        # We can have an instance of Sempahor, too, but this is not practical, since Journal can use its
        # own Semaphor.

        self.j = Journal(log_verbosity)
        # Verbosity tells the instance of John_Physics to ignore logs of higher verbosity than its own.
        # If you set verbosity to be low here, only important messages will be logged.
        # Of course, for every log, you can set the verbosity requirement manually.
        # A message will not be logged even if it satisfies the verbosity requirement if any of its parent
        # routines doesn't satisfy the verbosity requirement.
        # Typically, writes within subroutines are one level of verbosity higher than the subroutine itself.

        self.dj = Disk_Jockey(f"outputs/{self.ID}", self.j)
        self.dj.create_data_nodes({"system" : {"log" : "txt"}})
        # Disk Jockey requires a string to identify the subdirectory where it reads and writes data. This is
        # why the ID string is very important.
        # We pass our instance of Journal to Disk Jockey, and now Disk Jockey can use it to print to the log.
        # We can start out by creating some default, static part of data node structure. Here, there will
        # always be a subfolder ".../system/", with a file "log.txt".
        # More elements can be added to the node structure at any point: for example, each dataset can have
        # its own subfolder if it comes with multiple datafiles! Disk Jockey will read the actual node
        # structure on load from its root metadata file.
        # Note that all metadata files are by default .json except if the datafile is a .csv, in which case
        # the metadata has to be .pkl in order to store the column types. .pkl is very versatile, but .json
        # is human-readable. You can specify metadata filetypes by calling set_metadatum_type.

        self.string_solutions = {} # [dataset name] = solution

    def solve_string_theory(self, number_of_strings):

        self.j.enter(f"Solving string theory with {number_of_strings} strings...", 0)
        # Here we tell the Journal that we entered a new routine. All subsequent logs will be marked as
        # children of this routine until the exit method is called.

        self.j.write("Time to tie up some strings!", 5)
        # This message has verbosity 5, so it only logs if you set verbosity to 5 or higher!

        self.j.write("Asking mooses for help...", 1)
        # Time to enter a child routine and see what happens!
        self.enumerate_moose_friendship(6)

        self.j.write("Time to think really hard!", 1)
        # Here we show how powerful Sempahors are to log long processes. They update at user-specified
        # intervals and always estimate how long will it take for the process to finish. To start a semaphor
        # process, just use Journal.enter and pass semaphored = True together with the required kwargs.

        semaphor_msg = "Thinking about stringy cheese"
        # Every semaphor process has a header, so you don't forget what is the think eating your RAM.

        simulation_time_checkpoints = np.linspace(0, number_of_strings * number_of_strings, 100 + 1)
        # Semaphor processes are measured in simulation time, which can be any parameter you choose. By
        # passing an iterable of specific values, every time the current sim time exceeds another checkpoint
        # value, the Semaphor updates (so that if you update it very often, you don't waste time printing).
        # Note: In case of very frequent updates, disabling fancy printing will speed up the process.

        self.j.enter(semaphor_msg, 1, semaphored = True, tau_space = simulation_time_checkpoints)
        # The required kwarg is "tau_space", i.e. the sim time checkpoints. The naming convention is that
        # tau stands for simulation time and t stands for real time.

        result = np.zeros((number_of_strings, number_of_strings))

        for a in range(number_of_strings):
            for b in range(number_of_strings):
                # We do something very computationally heavy here, I think

                total = 0
                for i in range(1000):
                    for j in range(1000):
                        total += ((i + a) * (j + b)) % 97

                result[a][b] = total

                self.j.update_semaphor_event(a * number_of_strings + b)
                # Don't forget to update the semaphor with the current sim time!

        duration = self.j.exit("Evaluation")
        # By exiting we close the Semaphor process. We can add a little exit message. This exit uniquely
        # returns a value: the duration of the process measured in seconds, as a float.
        # Note that a semaphorised routine cannot log children routines!

        # Now, let us pass the result onto Disk Jockey. Let's create a new data node:
        data_group_name = f"{number_of_strings}_strings"
        self.dj.create_data_nodes({data_group_name : {"result" : "json"}})
        # The data group name should be unique: here I'm playing a dangerous game. Do better than this!

        # Now, let us store the data:
        self.dj.commit_datum_bulk(data_group_name, "result", result.tolist())
        self.dj.commit_metadatum(data_group_name, "result", {"duration" : duration})
        # The actual file is going to be a .txt, so string conversion it is. The metadata file is a .json,
        # and we can add datapoints to it until the point of writing to disk (which comes later!)

        # We should also store them internally for analysis, plotting etc.
        self.string_solutions[data_group_name] = result

        self.j.exit()


    def enumerate_moose_friendship(self, number_of_mooses, current_friendship = 1):
        # It is well known that two mooses meeting must be but fleeting, but when three mooses meet, they
        # stop and greet. This method uses tail recursion to calculate how many friendly greetings occur.

        self.j.enter(f"Calculating moose friendship with {number_of_mooses} mooses remaining...", 5)
        # Because the method is recursive, logging from inside can repeat many times. Better set the
        # verbosity to be high!

        if number_of_mooses == 0:
            self.j.write("No more mooses!")
            self.j.exit("End of tail!") # exit logs can have messages, too!
            return(current_friendship)
            # Make sure to firstly exit the routine in Journal, and only then terminate!

        magnified_friendship = self.enumerate_moose_friendship(number_of_mooses - 1, number_of_mooses + current_friendship)
        self.j.exit()
        return(magnified_friendship)

    def print_string_solutions(self):
        # A cheeky output function. Pretend these are nice plots and whatnot.
        self.j.enter("Printing calculated solutions...")
        for dataset_label, dataset_value in self.string_solutions.items():
            self.j.write(f"Result for dataset '{dataset_label}': {np.sum(dataset_value)}")
        self.j.exit()

    def save_data(self):
        # Here we tell Disk Jockey to save the committed data to disk

        self.dj.commit_datum_bulk("system", "log", self.j.dump())
        # First, we commit the current state of the Journal. Note that the internal dump looks a bit
        # different to what's in your terminal, with no fancy printing or Semaphor artifacts.
        self.dj.commit_metadatum_point("system", "log", "datasets", list(self.string_solutions.keys()))
        # We can add to existing metadata values datapoint by datapoint.

        self.dj.save_data()
        # We can specify which data groups to save, or save them all!

    def load_data(self):
        # Here, we simply tell Disk Jockey to load data from disk. Because it took notes last time, it now
        # knows exactly what files to load.

        self.j.enter("Loading data...", 0)

        self.dj.load_data()
        # Once again, we can restrict ourselves to loading only particular data groups. This can be very
        # useful: for example, I work on a script for computational chemistry, and sometimes I want to load
        # the calculated molecule properties without loading my old datasets, so I don't have to wait for the
        # program to perform costly calculation on the same molecule again. And those old datasets will wait
        # for me on the disk until I need to compare them to the new ones at any later point!

        # Of course, we still need to access the data. Let's save it to some internal property here.
        for dataset_label in self.dj.metadata["system"]["log"]["datasets"]:
            self.j.write(f"Restoring dataset {dataset_label}", 3)
            self.string_solutions[dataset_label] = np.array(self.dj.data_bulks[dataset_label]["result"])
        # As you can see, you still need to know the structure of the data in order to be able to interpret
        # it. With great freedom comes great flexibility!

        self.j.exit()


def saving_example():
    john = John_Physics("example")
    john.solve_string_theory(12)
    john.print_string_solutions()
    john.save_data()
    john.j.close_journal()
    # This de-buffers the highlighted row and prints out a dinkus. It would be better to have it automated in
    # some teardown routine of John_Physics!

def loading_example():
    john = John_Physics("example")
    john.load_data()
    john.solve_string_theory(10)
    # After loading old data, we can still add new data. Saving at the end stores both!
    john.print_string_solutions()
    john.save_data()
    john.j.close_journal()

# To see how this example works, firstly run the saving_example() function. Then, go see the contents of the
# outputs/ subdirectory which will be created. Then, comment out the saving_example() call and instead run
# the loading_example() function. Enjoy!

saving_example()
#loading_example()


