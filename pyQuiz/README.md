# Python Quiz Client
The python quiz client requires the python bindings for umundo 0.5.0. As these bindings are not present in the installer packages, they must be compiled from source. Please refer to the offical documentation: https://github.com/tklab-tud/umundo/blob/master/docs/BUILDING.md

# Installation
Besides python3, the client requires the python-tk package for the GUI and, if not installed by default, libpython.
Make sure the umundocore library is installed on the OS. For 64-bit linux based operating systems, the library umundo/libumundocore64.so can be copied into a suitable folder (e.g. /usr/local/lib). Don't forget to refresh the library cash via `ldconfig`.

# Running the application
Simply execute `python3 main.py` inside this folder.
