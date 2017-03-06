# Predictive Parking

This is a proof of concept for scan data analysis using a kibana dashboard.

Het in kaart brengen van de parkeerdruk door middel van scan data.
We zijn bezig met een proof of concept (POC)

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
 - make import more reliable
 - incremental data loading


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


NOTE
====

  - IF ELK5 fails to start / unknown host.. then RUN 'sysctl -w vm.max_map_count=262144'
    Elasticsearch 5 is WAY more strickt in checking the environment and memmory conditions
  - Memory consupmtion is HUGE by both elasticsearch and the database. You can lower memory
    consumption in the .jenkins/docker-compose file
