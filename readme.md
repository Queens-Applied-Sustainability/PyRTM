#pyrtm

Python wrapper around three open-source Radiative Transfer Modelling
applications.

##Status

Still in the preliminary stages of construction, something like v.0.0.0.0.2.

###Driver/wrapper/config thing

####Completed

 * Data structure for input configuration

####To Do

 * Make input data structure subclass `dict` for some cool features.
 * Write YAML importer for non-default run settings
 * Flesh out the inputs a bit more and genericize for all RTM scripts (currently
   it's SBDART-biased).

###SBDART

####Completed

 * Generate input file (Fortran NAMELIST format)
 * Call executable from command line

####To Do

####Challenges

 * How to parallelize? The executable looks for a hard-coded input file name in
   the directory where it resides.
   
     * Copy the executable to a new folder to run a parallel task?
     * Edit the fortran code to take command-line arguments for in/out files?

###SMARTS



