# Objects Route Analysis

### Description
User gives json file with routes data.

    {
        "idObject": 1,
        "idPath": 1,
        "points": [
            {
                "x": 835.1869348778753,
                "y": 945.6047962927408,
                "time": 280.7413231708063
            },
            {
                "x": 830.853954933912,
                "y": 948.5347862574193,
                "time": 281.32719209734313
            },
            ...
    }

Points represent the route (idPath=1) completed by object (idObject=1). <br>
There can be any number of routes in input json file. <br>
(idObject, idPath) pairs should be unique. <br>

User wants to set parameters such as:
* rectangle area defined by two points: (x1, y1), (x2, y2)
* time range: (t1, t2) <br>

and get the time of every entrance and every exit from this area for each idObject 
and each idPath. <br>
The following output <br>
`Id Object;Id Path;Entries and exits`<br>
`1;14; [[212.96, 215.18]`<br>
`2;5; [[None, 314.65]]`

means that for given time range:
* idObject:1, idPath14 entered the area at 212.96 and went out at 215.18
* idObject:2, idPath5 didn't enter the area (he was already there) and went out at 215.18.


### What is done?
* `Document` class with methods for processing the input json (routes' data).
The main methods are:
  * `split_input_json_data()` - split input json into json files each 
  corresponding to a single route.
  * `update_routes_with_entries_exists_info()` - looks for each route whether 
  the given area was entered or went out; update every json file from
  split jsons with this information.
  * `clear_routes_from_entries_exists_data()` - remove entries and exits data 
  from split json files. 
  * `get_results()` - collect entries and exits data from split json and write 
  it to output file.
  
* Multiprocessing mode - the above methods can be performed both with usage of
basic "for loop" or with processes.

* `logger.py` - tool for logging. Consists of 2 methods:
  * `log()` - used to print log to console and save it to a given file.
  * `timer_func()` - decorator that measures execution time for function
  being decorated. <br>
Example lines from log file: <br>
`[13:46:47]	--- New document temp\paths3_rand100` <br>
`[13:46:52]	Function 'split_input_json_data' executed in 5.6135 seconds; multiprocessing: True`<br>
`[13:46:57]	Function 'update_routes_with_entries_exists_info' executed in 4.6483 seconds; multiprocessing: True`<br>
`[13:47:4]	Function 'get_results' executed in 6.9089 seconds; multiprocessing: True`<br>

* Running script from `cmd` with `ProcessDocument.py`: <br>
  For example: <br>
  `python ProcessDocument.py -MD paths.json 830 940 840 950 250 350` <br>
where: <br>
`M` - multiprocessing mode, <br>
`D` - draw routes and save as image file, <br>
`830 940 840 950 250 350` - parameters x1, y1, x2, y2, t1, t2 respectively.

* Flask application `WebApp.py` (for more user-friendly experience):
  * choose json file,
  * list all routes from json file with ability to plot up to 30 routes,
  <br> (even before setting parameters)
  * set parameters,
  * get results in table format.

---------
### TODO:
* Plot routes in multiprocessing mode
<br> (to be able to plot more than 30 routes in a reasonable amount of time),
* Clear temp folder more clever
<br> (not to just clear it every time right before the new document initialization)
* "Mini-Paint" in `WebApp.py` (for even more user-friendly experience) <br>
User can draw rectangle area right on the plotted routes. 
Next, coordinates of this rectangle are propagated to set_parameters method.

