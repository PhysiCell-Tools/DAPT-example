# PhysiCell DAPT Example

This repository shows several examples of how to use the [Distributive Automated Parameter Testing](https://github.com/BenSDuggan/DAPT) (DAPT) package with [PhysiCell](https://github.com/MathCancer/PhysiCell) version 1.7.0.  DAPT makes parameter testing easy by making it easy to use APIs (e.g. Google Sheets and Box) to build a pipeline.  By connecting to "Databases", these tests can be run by many people simultaneously.  This repository contains examples of a simple example ([basic.py](basic.py)), example with a configuration file ([config.py](/config.py)), and an example using Google Sheets ([sheets.py](/sheets.py)).  

The PhysiCell biorobots sample project is used in this tutorial.  You can interact with this model using the [biorobots NanoHub tool](https://nanohub.org/tools/pc4biorobots).  This sample project has three types of agents: cargo cells (blue), worker cells (red), and director cells (green).  The worker cells will move to cargo cells, attach to them, move the cargo cells to the directory cells, drop off them off, and then look for another cargo cell.  

Two important parameters for this model are `attached_worker_migration_bias`, the motility bias when worker cells are attached to cargo cells, and `unattached_worker_migration_bias`, the motility bias when worker cells aren't attached to cargo cells.  When the bias is 1, the worker cells' strictly follow the chemotaxis signal, and when it's 0, the worker cell's motility direction is random.  Bias between 0 and 1 change how biased the migration towards random or deterministic motion.

For these examples, three tests will be ran.  The first, `default`, uses the default parameters.  The second test, `attached-random`, sets unattached migration bias to 1 and attached bias to 0.1.  The third test, `unattached-random`, sets unattached migration bias to 0.1 and attached bias to 1.  A third parameter, `max_time` is included which allows the simulation time to easily be changed.  The bellow examples show how DAPT can be used to test these parameters.

## Setup instructions

Before setting up these examples, make sure that you can run PhysiCell by consulting the [Quickstart Guide](https://github.com/MathCancer/PhysiCell/blob/master/Quickstart.pdf).  Once you have confirmed that you can compile and run PhysiCell, open Terminal or CMD and type the following:

```
git clone https://github.com/BenSDuggan/PhysiCell_DAPT_Example
make -C PhysiCell_DAPT_Example/PhysiCell
pip install dapt
```

## Repository contents

```
.
├── outputs                         # Directory where output from the pipeline is saved
├── PhysiCell                       # PhysiCell 1.7.0 source code
├── basic.py                        # Simplest example using DAPT with PhysiCell
├── config.py                       # Example of using config file with DAPT
├── sheet.py                        # Example showing how to combine cloud services like Google Sheets with DAPT
├── reset.py                        # Python script that removes files created by examples
└── parameters.csv                  # Parameters used for by each example, not used directly
```

## Basic Example

The simplest way to use DAPT is with a delimiter-separated file, such as a CSV.  CSVs are common files used to store two-dimensional data, typically with a header.  This makes them natural to use as a "database", where rows are tests and columns are the attributes.

### PhysiCell Settings

PhysiCell allows domain, microenvironment, and user parameters to be defined in an XML file named [PhysiCell_settings.xml](PhysiCell/config/PhysiCell_settings.xml).  This allows different settings to be run without recompiling PhysiCell.  The `user_parameters` tag contains the `attached_worker_migration_bias` and `unattached_worker_migration_bias` variables we are interested in.  The attached migration bias can be represented from the root of the XML tree as `./user_parameters/attached_worker_migration_bias`.  If that representation of PhysiCell variables is used, then new values in the XML can be set by adding its path as an attribute to the database.  The `create_XML()` method in `basic.py` takes a dictionary of attributes with the path from root as keys.  It updates the XML settings using the value associated with each key.  The `create_XML()` method was copied from `dapt.tools.create_XML()`.  Using this approach, it is easy to add or remove variables from the settings.


The parameters used for this (and the other examples) are shown in the table below.  The table has three tests (one per row) named default, attached-random, and unattached-random, using the `id` attribute.  The `status` attribute can be updated to reflect what task is currently in progress and needs to be empty initially for the test to be ran.  The `start-time` and `end-time` attributes are set when the test begins and ends, respectively.  The `comment` attribute can be set before, during, or after a test is ran to provide additional information.  The attributes to the right of `comment` are used for the PhysiCell biorobots sample project settings.

| id                | status | start-time | end-time | comment | ./overall/ max_time | ./user_parameters/ attached_worker_migration_bias | ./user_parameters/ unattached_worker_migration_bias |
|-------------------|--------|------------|----------|---------|--------------------|--------------------------------------------------|----------------------------------------------------|
| default           |        |            |          |         | 2880               | 1.0                                              | 0.5                                                |
| attached-random   |        |            |          |         | 2880               | 0.1                                              | 1.0                                                |
| unattached-random |        |            |          |         | 2880               | 1.0                                              | 0.1                                                |

This table is saved in [parameters.csv](/parameters.csv) and used by [basic.py](/basic.py).  This file isn't modified by the script.  The contents are copied to a file named `basic_params.csv` so the master database doesn't get overwritten.  Run the script (`python basic.py`) and observe the results.  The outputs folder now contains three final output SVGs from the script.

Before explaining how the script works, you should look at it yourself to get an overview.  The script is broken into three blocks: `main()`, `create_XML()`, and calling `main()`.  

The first part of the script is importing all of the modules that will be needed.

```
import os, platform, csv, shutil, dapt
import xml.etree.ElementTree as ET
```

Next, the `main(db_path)` function is defined.  This function is responsible for setting up and running the tests.  It uses the `db_path` variable, which is the path to `basic_params.csv`.  The database and parameter object can then be created.  The first parameters can be retrieved from the database using the `dapt.Param.next_parameters()` method.

```
db = dapt.Delimited_file(db_path, delimiter=',')
ap = dapt.Param(db, config=None)

parameters = ap.next_parameters()
```

The next part of the code tests parameters until there are no more.  The parameters are tested in a `try`/`except` block to catch errors that occur.  If an error occurs, the `status` attribute for that test is set as `failed` and the `comment` attribute will contain the error.  The last part of the loop fetches the next parameter.  If there are no more parameters to run, the `dapt.Param.next_parameters()` method will return `None` and the loop will break.  Bellow is the code block that runs each parameter, with the testing code removed.

```
while parameters is not None:
    print("Request parameters: %s" % parameters)

    try:
        # Testing code here
        pass

    except ValueError:
        print("Test failed:")
        print(ValueError)
        ap.failed(parameters["id"], ValueError)

    parameters = ap.next_parameters()
```

The `try` block, contains the main pipeline code.  There are four steps: clean the PhysiCell directory, change the parameters in the PhysiCell settings file, run the simulation, and copy the data to a new directory.  For each of these steps, the status of the database is updated to reflect which step is currently in progress.  This makes it easy to monitor what step the pipeline is on.  After the test is complete, the parameters must be marked as successful or failed.

```
# Reset PhysiCell from the previous run using PhysiCell's data-cleanup
print("Cleaning up folder")
ap.update_status(parameters['id'], 'clean')
os.system("make data-cleanup")

# Update the default settings with the given parameters
print("Creating parameters xml")
ap.update_status(parameters['id'], 'xml')
create_XML(parameters, default_settings="config/PhysiCell_settings_default.xml", \
           save_settings="config/PhysiCell_settings.xml")

# Run PhysiCell (execution method depends on OS)
print("Running test")
ap.update_status(parameters['id'], 'sim')
if platform.system() == 'Windows':
    os.system("biorobots.exe")
else:
    os.system("./biorobots")

# Moving final image to output folder
ap.update_status(parameters['id'], 'output')
shutil.copyfile('output/final.svg', '../outputs/%s_final.svg' % parameters["id"])

# Update sheets to mark the test is finished
ap.successful(parameters["id"])
```

Using this approach, additional steps can easily be added.  For example, if you wanted to convert the final image to a PNG you could add the following lines after the image is saved and before `ap.successful()` is called.  This requires [ImageMagick](https://imagemagick.org/index.php) to be installed.

```
# Convert output SVG to PNG
ap.update_status(parameters['id'], 'img-proc')
os.system("mogrify -format png -path ../outputs ../outputs/%s_final.svg" % parameters['id'])
```

The last part of the code resets the database and runs the main function.  The directory is changed to [PhysiCell](/PhysiCell) so the executable is easier to run.  This means that paths to the CSVs file must be moved up a directory (as the script is effectively ran inside the PhysiCell folder).    The last step is to run the `main()` method.

```
if __name__ == '__main__':
    os.chdir('PhysiCell')

    master_db_path = '../parameters.csv'
    db_path = '../basic_params.csv'

    shutil.copyfile(master_db_path, db_path)

    main(db_path)
```

## Config Example


## Sheets Example


## Cleanup

To cleanup the directory, you can run the [reset.py](/reset.py) script.  This script will remove the finals in the outputs folder, cleanup the data created by PhysiCell, and remove the CSVs used by the example scripts, except for [parameters.csv](/parameters.csv).  To remove the `.o` and executable file created by PhysiCell you can include the `--hard` flag (`python reset.py --hard`).
