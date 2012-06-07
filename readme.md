#pyrtm

Python wrapper around three open-source Radiative Transfer Modelling
applications.

##Status

Still in the preliminary stages of construction, something like v.0.0.0.0.3.

###SMARTS

Batch file processing was turned on in the source code (line 189 in
`smarts295.f`, `       batch=.TRUE.`) before compiling. The binary contained in
this package was then compiled with speed optimizations using gfortran:

    $ gfortran smarts295.f -Ofast -o smarts295

The executable was built on a 64-bit Ubuntu machine. Not sure if it will work
straight-up on a 32-bit machine or other platform, but replacing the executable
with one for your platform should be fairly straight-forward.


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
