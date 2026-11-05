# project-management-utils
Utilities for managing research project software: logging, dataset control, disk access, routine duration estimation, access point script generation.

# Integration
This repository is intended to be integrated into your project as a submodule.

## Adding the submodule
Let's say we want to place the scripts into a subdirectory /utils. In your project directory, run the following commands:

```console
git submodule add https://github.com/michael-horansky/project-management-utils utils
git add .gitmodules utils
```

The submodule is now registered in .gitmodules with its directory. Commit the change and push to push the submodule integration upstream.

## Updating the submodule
To bring your local copy of the utils submodule up-to-date, run the following command from your project repository:

```console
git submodule update --remote utils
```

To push the submodule update upstream, add the submodule directory, then commit and push your main repository as usual.

## Cloning your project
Since your project now contains a submodule, you need to explicitly state the inclusion of the submodule when cloning your project repository like so:

```console
git clone --recurse-submodules \[your project repository\]
```

# Using Project Management Utilities
This section outlines in brief the functionalities of each module of utils. For more detailed tutorials, please visit the [demo repo](https://github.com/michael-horansky/project-management-utils-demo).

## Journal
Structured and annotated log for your script. For examples of major functionalities call Journal.sample_behaviour in an empty script.

### Structured writing
- write(msg, v, ...): Write a message to output stream in the current routine if current verbosity level isn't smaller than v.
- enter(header, v, semaphored, ...): Enter a routine if current verbosity level isn't smaller than v. For semaphors, see below.
- exit(): Exit current routine.

### Semaphors
Semaphors allow you to attach progress bars to routines which are displayed on the current line. You can stack multiple progress bars and write new logs asynchronously of the progress bars within the routine. The progress bars estimate the time of finish based on simulation time data you provide.
- enter(... semaphored=True, max\_tau, flush\_every\_update=True): A progress bar is shown until the routine is exited. max\_tau determines the maximum sim time, assuming zero at start. If flush\_every\_update, the sim time is printed in the progress bar and a write is performed on every update, not just on change of progress percentage. Returns semaphor ID.
- update\_semaphor\_event(tau=None, ID=None): Updates sim time for semaphor at ID. If no ID is provided, the most recently added semaphor (deepest in the stack) is updated. If no sim time is provided, an increase by 1.0 is assumed for the purposes of loop counting.
- ```semaphor\_event\_overtime(tau=None, ID=None)```: Adds overtime to semaphor at ID. Overtime is elapsed sim time which was not previously anticipated, and this is added to max\_tau. If no ID is provided, the most recently added semaphor (deepest in the stack) is updated. If no overtime is provided, a value of 1.0 is assumed for the purposes of loop counting.

# Requirements
The following Python 3 libraries are required:
- pathlib
- csv
- base
- json
- numpy
- pickle
- time
