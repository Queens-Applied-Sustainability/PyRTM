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

##Licensing

###Third-Party RTM Software Packages

The use of any code and/or executable residing in any of the `exe` and `src`
folders is subject to the licenses of their respective projects. You MUST accept
(and in some cases register) with their owners before using.

 * [SBDART](http://arm.mrcsb.com/sbdart/)
 * [SMARTS](http://www.nrel.gov/rredc/smarts/)
 * [RRTM](http://rtweb.aer.com/rrtm_frame.html)

Licenses for those softwares are included in some cases in this repository only
for convenience and quick reference. The licenses on the above linked pages
always takes precedence.

###pyrtm Python Modules

Python code developed for the [Queen's University Applied Sustainability
Research Group]
(http://www.appropedia.org/Category:Queens_Applied_Sustainability_Group) is
released under the [GNU General Public License v3]
(http://www.gnu.org/licenses/gpl.html).
