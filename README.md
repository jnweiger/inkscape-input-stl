# inkscape-input-stl
Input extension for inkscape to read stl files sliced into layers. Requires slic3r

## Linux Installation
* Install slic3r from https://dl.slic3r.org/linux
* clone, download a zip or view raw, save the input-stl.py and input-stl.inx files.
* Move them into the folder ~/.config/inkscape/extensions
* Restart inkscape.
* Use import and select 'Files of type: All Inkscape Files' -- STL files should be visible e.g. in the test folder of this repo.
* Try import an *.stl file the import dialog should open.
* On the second tab of the import dialog adjust the command name of slic3r, if you installed it in a nonstandard location.
If there is an error message instead of the STL import dialog, check the file ~/.config/inkscape/extension-errors.log

## Windows Installation
* Make sure you installed inkscape from inkscape.org via their msi install wizard. The inkscape from the windows appstore does not load any extensions.
* Install slic3r from https://dl.slic3r.org/win
* Download https://github.com/jnweiger/inkscape-input-stl/archive/master.zip, extract the input-stl.py and input-stl.inx files.
* Move the two files to C:\Program Files\Inkscape\share\extensions
* Restart inkscape.
* Use import, and select 'Files of type: All Inkscape Files' -- STL files should be visible e.g. in the test folder of this repo.
* Try import an *.stl file, the import dialog should open.
* On the second tab of the import dialog adjust the command name to slic3r-console.exe and add the path, if you installed it in a nonstandard location.

If there is an error message instead of the STL import dialog, check the file AppData\Roaming\inkscape\extension-errors.log
