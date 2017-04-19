# Predictive Parking

This is a project about the scan data analysis. Making maps of the parking "pressure" 
in the city is the main goal.

The project is devided in a few docker-containers with their own functions.

  - api
     - provide web api on scan data
     - contains database building / migrations and loading of related databases
  - csvimporter
    - golang code which crunches to and cleans up scan data and import csv data into postgres database
  - kibana
    - default kibana to analyse scan - data. deployed at: https://acc.parkeren.data.amsterdam.nl
  - logstash
    - import data from database into elasticsearch
  - kibanawegdeel
    - POC showing proof of concept with parking pressure: https://demo1.atlas.amsterdam.nl/goto/a6ec13ad0c9c4b2f2e5539cdf1d57feb
  - postgres
    - database docker with custom settings
  - .jenkins
    - import environment to build new dataset


There are two steps

 - 1. Prepare the data
 - 2. Visualize the data in kibana

https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:pparking:architectuur


 Step 1. Preparing the data
==========================

We take data from a few sources and create a dataset usable for predictive parking analysis.

Source data:
 - all known parking spots.
 - all known roads. (wegdelen) / partial roads. (weddelen)
 - all known neigborhoods. (buurten)
 - all 39.5 milion cars scans of 2016.

We combine all data sources in a postgres database table
in `scan_scans` which contains all scans
normalized with parkingspot, neighborhood and road information.
All this data is indexed in elasticsearch and that allows us to create a
kibana dashboard.

The kibana project has one customized view with loads out vector data of roads, neighborhood and
parkingspots and allows us to create dynamic maps.

In the `.jenkins` folder is the `import.sh` which triggers all the needed build steps.

Local development can be done using `docker-compose up database elasticsearch`.


 Step 2. Visualizing the data
=============================


To get quick results and vast visualizations we choose kibana on top of elastic search.

We use a dockerized logstash instance to load the postgres database `scans_scan` into
elastic index.

The visuallizations are done with 2 different kibana instances. We use 2 because the plugins
`enhanced_tilemap` does not play well together with other custom map plugins. `kibana-plugin-parkeren`



 TODO
=====

 - add test
 - incremental data loading
 - make custom api to replace kibana.


Development
===========


 Step1, Data preparation:
----------------------------


  - set environment variables TESTING=no/yes , ENVIRONMENT=acceptance, and
    PARKEERVAKKEN_OBJECTSTORE password.

  - RUN .jenkin/import.sh


Tips.

  - Downloads are cached in named volumes. Database downloads, zips and csv's are saved.
    forcefull remove the named volume (pp_unzip-volume) if it contains the wrong data.
    When TESTING = no the `unziped` will be deleted



Step2, Visualization
----------------------------

   There is a `normal` kibana and a special `kibanawegdeel`
   both work similiar.

   - The Dockerfile in each project defines which plugins are loaded into
     kibana and some settings
   - start a local accesible elasticsearch docker with parking data from step1.
   - for plugin development npm is used and I suggest looking into the pluging develop
     ment documentation pages of kibana
