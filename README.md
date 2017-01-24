# Predictive Parking

This is a proof of concept for scan data analysis using a kibana dashboard.

Het in kaart brengen van de parkeerdruk door middel van scan data.
We zijn bezig met een proof of concept (POC)


https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:pparking:architectuur


We take data from a few sources and create a dataset usable for predictive parking analysis.

Source data:
 - all know parking spots.
 - all know roads. (wegdelen) / partial roads.
 - all know neigborhoods.
 - all 31+ milion cars scans of 2016.
 
We combine this data in a postgres database table in `scan_scans` which contains all scans
normalized with parkingspot, neighborhood and road information.
All this data get's indexed in elasticsearch and that allows us to create a 
kibana dashboard.
 
The kibana project has one customized view with loads out vector data of roads, neighborhoos and 
parkingspots and allows us to create dynamic maps.
 
In the `.jenkins` folder is the `import.sh` which triggers all the needed build steps.
 
Local development can be done using `docker-compose up database elasticsearch`.
