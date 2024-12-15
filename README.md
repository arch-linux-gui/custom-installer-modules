# ALG Custom Installer Modules

Custom Installer Modules for ALG aim to add additional functionality to the installer specific to ALG. The modules are to be installed in the same directory as other modules, which is <code>etc/calamares</code>. For prototyping, the modules will first be written in python, and then C++/Qt when the features are finalised.

Tests are in /src/tests.

Run tests with `PYTHONPATH=./src python3 -m unittest discover -s tests`

## How to use modules?

Ideally, modules are invoked in <code>settings.conf</code>. Some modules have a dependency on the other, for example, <i>packages_remover</i> will work correctly if it has GS values from <i>hardware_detection</i>. Hence it totally makes sense to call hardware_detection before packages_remover.

## Todo - Migrate Shell Processes

Currently there are certain script in ALG's code that reside in </code>/usb/local/bin</code>, which are run by calamares shellprocess. These have to migrate here.

Also, a module for choosing editions needs to be made that will pass values to <i>packages_remover</i>.
