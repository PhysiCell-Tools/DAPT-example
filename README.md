# PhysiCell DAPT Example

This repository shows several examples of how to use the [Distributive Automated Parameter Testing](https://github.com/BenSDuggan/DAPT) (DAPT) package with [PhysiCell](https://github.com/MathCancer/PhysiCell) version 1.7.0.  DAPT makes parameter testing easy by making it easy to use APIs (e.g. Google Sheets and Box) to build a pipeline.  By connecting to "Databases", these tests can be run by many people simultaneously.  This repository contains examples of a simple example ([basic.py](basic.py)) and example with a configuration file ([paper_example.py](/paper_example.py)).

The PhysiCell biorobots sample project is used in this tutorial.  You can interact with this model using the [biorobots NanoHub tool](https://nanohub.org/tools/pc4biorobots).  This sample project has three types of agents: cargo cells (blue), worker cells (red), and director cells (green).  The worker cells will move to cargo cells, attach to them, move the cargo cells to the directory cells, drop off them off, and then look for another cargo cell.  

Two important parameters for this model are `attached_worker_migration_bias`, the motility bias when worker cells are attached to cargo cells, and `unattached_worker_migration_bias`, the motility bias when worker cells aren't attached to cargo cells.  When the bias is 1, the worker cells' strictly follow the chemotaxis signal, and when it's 0, the worker cell's motility direction is random.  Values between 0 and 1 allow cell motion to span between completely random and completely deterministic motion.

For these examples, three tests will be run.  The first, `default`, uses the default parameters.  The second test, `attached`, sets unattached migration bias to 1 and attached bias to 0.1.  The third test, `unattached`, sets unattached migration bias to 0.1 and attached bias to 1.  A third parameter, `max_time` is included which allows the simulation time to easily be changed.  The examples below show how DAPT can be used to test these parameters.

## Setup instructions

Before setting up these examples, make sure that you can run PhysiCell by consulting the [Quickstart Guide](https://github.com/MathCancer/PhysiCell/blob/master/Quickstart.pdf).  Once you have confirmed that you can compile and run PhysiCell, open Terminal or CMD and type the following:

```
git clone https://github.com/PhysiCell-Tools/DAPT-example
cd DAPT-example
make
pip install dapt
```

## Repository contents

```
.
├── backup                          # Stores backup of config and parameters to reset examples
├── basic.py                        # Simplest example using DAPT with PhysiCell
├── outputs                         # Directory where output from the pipeline is saved
├── paper_example.py                # Example used in the paper demonstrating use of a config file with DAPT
└── parameters.csv                  # Parameters used for by each example, not used directly
```

## How to run an example

Each of the examples can be ran in the same way.  The Python script you run will change depending on which example you are running.  To run an example, type the following commands into the terminal from inside the root directory.

1. `make reset` (resets the DAPT example to how they originally came)
2. `make` (builds PhysiCell)
3. `python [example name]` (e.g. `python paper_example.py`)

The data generated by PhysiCell will be placed in the output folder.

To reset completely after running an example, run the following commands in the terminal from inside the root directory. *This is **not required** between runs* but is noted for completion. 

- `make data-cleanup` (removes data generated from simulation)
- `make clean` (removes object and executable files)
- `make reset` (resets the DAPT example to how they originally came)

## Basic Example

The simplest way to use DAPT is with a delimiter-separated file, such as a CSV.  CSVs are common files used to store two-dimensional data, typically with a header.  This makes them natural to use as a "database", where rows are tests and columns are the attributes.  This example is by executing 'python basic.py'.

### PhysiCell Settings

PhysiCell allows domain, microenvironment, and user parameters to be defined in an XML file named [PhysiCell_settings.xml](PhysiCell/config/PhysiCell_settings.xml).  This allows different settings to be run without recompiling PhysiCell.  The `user_parameters` tag contains the `attached_worker_migration_bias` and `unattached_worker_migration_bias` variables we are interested in.  The attached migration bias can be represented from the root of the XML tree as `./user_parameters/attached_worker_migration_bias`.  If that representation of PhysiCell variables is used, then new values in the XML can be set by adding its path as an attribute to the database.  The `create_XML()` method in `basic.py` takes a dictionary of attributes with the path from root as keys.  It updates the XML settings using the value associated with each key.  The `create_XML()` method was copied from `dapt.tools.create_XML()`.  Using this approach, it is easy to add or remove variables from the settings.


The parameters used for this (and the other examples) are shown in the table below.  The table has three tests (one per row) named default, attached, and unattached, using the `id` attribute.  The `status` attribute can be updated to reflect what task is currently in progress and needs to be empty initially for the test to be ran.  The `start-time` and `end-time` attributes are set when the test begins and ends, respectively.  The `comment` attribute can be set before, during, or after a test is ran to provide additional information.  The attributes to the right of `comment` are used for the PhysiCell biorobots sample project settings.

| id                | status | start-time | end-time | comment | ./overall/ max_time | ./user_parameters/ attached_worker_migration_bias | ./user_parameters/ unattached_worker_migration_bias |
|-------------------|--------|------------|----------|---------|--------------------|--------------------------------------------------|----------------------------------------------------|
| default           |        |            |          |         | 2880               | 1.0                                              | 0.5                                                |
| attached          |        |            |          |         | 2880               | 0.1                                              | 1.0                                                |
| unattached        |        |            |          |         | 2880               | 1.0                                              | 0.1                                                |

This table is saved in [parameters.csv](/parameters.csv) and used by the example code.  This file is modified by the script and needs to be reset after running the code.  Run the script (`python basic.py`) and observe the results.  The outputs folder now contains three final output SVGs from the script.  To reset the parameters, run `make reset`.

Before explaining how the script works, you should look at it yourself to get an overview.  The script is broken into two blocks: `create_XML()` and the testing pipeline.  

The first part of the script is importing all of the modules that will be needed.

```
import csv, os, platform, shutil
import xml.etree.ElementTree as ET
import dapt
```

After defining the `create_XML()` method, the main pipeline starts.  The database and parameter object then get created.  These classes allow us to interact with the parameter space.  The first parameters can be retrieved from the database using the `dapt.Param.next_parameters()` method.

```
db = dapt.Delimited_file(db_path, delimiter=',')
params = dapt.Param(db, config=None)

p = params.next_parameters()
```

The next part of the code tests parameters until there are no more.  The parameters are tested in a `try`/`except` block to catch errors that occur.  If an error occurs, the `status` attribute for that test is set as `failed` and the `comment` attribute will contain the error.  The last part of the loop fetches the next parameter.  If there are no more parameters to run, the `dapt.Param.next_parameters()` method will return `None` and the loop will break.  Below is the code block that runs each parameter, with the testing code removed.

```
while p is not None:
    print("Request parameters: %s" % p)

    try:
        # Testing code here
        pass

    except ValueError:
        print("Test failed:")
        print(ValueError)
        params.failed(p["id"], ValueError)

    p = params.next_parameters()
```

The `try` block, contains the main pipeline code.  There are four steps: clean the PhysiCell directory, change the parameters in the PhysiCell settings file, run the simulation, and copy the data to a new directory.  For each of these steps, the status of the database is updated to reflect which step is currently in progress.  This makes it easy to monitor what step the pipeline is on.  After the test is complete, the parameters must be marked as successful or failed.

```
# Reset PhysiCell from the previous run using PhysiCell's data-cleanup
print("Cleaning up folder")
params.update_status(p['id'], 'clean')
os.system("make data-cleanup")

# Update the default settings with the given parameters
print("Creating parameters xml")
params.update_status(p['id'], 'xml')
create_XML(p, default_settings="backup/PhysiCell_settings.xml", save_settings="PhysiCell_settings.xml")

# Run PhysiCell (execution method depends on OS)
print("Running test")
params.update_status(p['id'], 'sim')
if platform.system() == 'Windows':
    os.system("biorobots.exe")
else:
    os.system("./biorobots")

# Moving final image to output folder
params.update_status(p['id'], 'output')
shutil.copyfile('output/final.svg', '%s_final.svg' % p["id"])

# Update sheets to mark the test is finished
params.successful(p["id"])
```

Using this approach, additional steps can easily be added.  For example, if you wanted to convert the final image to a PNG you could add the following lines after the image is saved and before `ap.successful()` is called.  This requires [ImageMagick](https://imagemagick.org/index.php) to be installed.

```
# Convert output SVG to PNG
ap.update_status(p['id'], 'img-proc')
os.system("mogrify -format png -path . outputs/%s_final.svg" % p['id'])
```

## Paper Example

This is the example used in the DAPT paper.  It differs from the basic example in that it removes clutter and demonstrates the `Config` class.  Specifically, the `create_XML()` method is replaced by DAPT's method, the `try/except` block is removed, and the final output image is no longer saved.

The `Config` class uses a JSON file to instructions on how DAPT should run.  In this example, the config is stored in a file named [config.json](/config.json).  Most classes accept a `Config` object and allow variables to be defined in the configuration, instead of in code.  The code block below shows how a `Config` class gets defined and used.

```
config = dapt.Config(path='config.json')
db = dapt.db.Delimited_file('parameters.csv', delimiter=',')
params = dapt.Param(db, config=config)
```

The config file in this example has two options: `{"last-test": null, "num-of-runs": -1}`.  The `last-test` setting is used to restart the last test you worked on if you quit DAPT.  The `num-of-runs` option defines the number of tests you would like to run.  For this example, all tests are being run (-1).

This example will overwrite the data produced when the next test is started.  To save the final SVG output, add `shutil` to the import list.  Then insert `shutil.copyfile('output/final.svg', '%s_final.svg' % p["id"])` on line 19, before the next parameter set is retrieved.
