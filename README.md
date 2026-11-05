# project-management-utils
Utilities for managing research project software: logging, dataset control, disk access, routine duration estimation.

# Integration
This repository is intended to be integrated into your project as a submodule.

## Adding the submodule
Let's say we want to place the scripts into a subdirectory /utils. In your project directory, run the following commands:

>git submodule add https://github.com/michael-horansky/project-management-utils utils
>git add .gitmodules utils

The submodule is now registered in .gitmodules with its directory. Commit the change and push to push the submodule integration upstream.

## Updating the submodule
To bring your local copy of the utils submodule up-to-date, run the following command from your project repository:

>git submodule update --remote utils

To push the submodule update upstream, add the submodule directory, then commit and push your main repository as usual.

## Cloning your project
Since your project now contains a submodule, you need to explicitly state the inclusion of the submodule when cloning your project repository like so:

>git clone --recurse-submodules \[your project repository\]

```console
foo@bar:~$ whoami
foo
```

# How to use?
Go to example.py and read through the source. The annotation will teach you how to use all main functionalities of the three provided modules.

# Requirements
The following Python 3 libraries are required:
- pathlib
- csv
- base
- json
- numpy
- pickle
- time
