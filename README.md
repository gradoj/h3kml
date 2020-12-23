# h3kml

Python script to generate Uber H3 hex grids to be displayed on Google Earth dynamically. Google Earth has Network Links https://developers.google.com/kml/documentation/kml_tut#network-links that are really intended to call an external webserver. This script uses the internal Python webserver on your local machine. It could be setup to run externally on a proper webserver but it is not currently. This would be nice as you wouldn't need to install python or any dependancies. I would not expose this server to the external world.

Requirements

Python 3
Uber H3 for Python https://github.com/uber/h3-py
Simplekml https://readthedocs.org/projects/simplekml/

How to Run

Run the python script with 'python3 h3kml.py 8000'
Double click or open h3kml.kml to make the connection from Google Earth.

This is running with Google Earth set to meters and all other default settings.
