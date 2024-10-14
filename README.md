# ALG Custom Installer Modules

Custom Installer Modules for ALG aim to add additional functionality to the installer specific to ALG. The modules are to be installed in the same directory as other modules, which is <code>etc/calamares</code>. For prototyping, the modules will first be written in python, and then C++/Qt when the features are finalised.

Tests are in /src/tests.

Run tests with `PYTHONPATH=./src python3 -m unittest discover -s src/tests`
