# microelectronica

Link to repo: https://github.com/slealq/microelectronica

## Notes about `tarea_regexp` folder

- `tarea_regexp` should contain two folders: `hier`, and `flat`, or any other synth type names.
- Inside each of the subfolders, there should be the reports.

## Steps to execute:

- Clone the repository
- Place the folder, with name `tarea_regexp` in the same path as the script
- Run the script with `./regex.py`. You should now see a new file called `report.csv` on your directory. This is the report.

## Note about % area diff

- It made more sense to me, to have a percentage of change of the current synth mode, vs the other synth mode.
- Example:
    
     `flat area` = 30
     
     `hier area` = 40
     
     In flat synth row: `% area diff` = (`flat_area` - `hier_area`) * 100 / `hier_area` = - 25 %
     
     In hier synth row: `% area diff` = (`hier_area` - `flat_area`) * 100 / `flat_area` = 33.333 %

     So read the `% area diff`, as how this area changes with respect to the other. If this is not accepted, the code that needs to change is between line 157 and 160 of `regex.py`.
