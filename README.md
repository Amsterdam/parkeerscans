# Overview

                       +-------------+
                       |parkeer scans|    4.000.000 A month
                       +------+------+
                              |
                              |
       +-------------------+  |
       |BGT kaart gegevens +--+
       +-------------------+  |
                              |      +------------+
                              +------+parkeerkaart|
                              |      +------------+
           +------+           |
           | BAG  +-----------+
           +------+           |
                              |
                              |
                       +-------v---------+
                       |                 |  in blocks of 500.000
    +------------------+  Database       |
    |                   |                 |
    |                   +-------+---------+
    +--v------+                   |
    |   API   |                   |
    +---+-----+                   v
    ^                 +-------+---------+
    |                 |                 |
    +-----------------+  Elsticsearch   |
                      |                 |
                      +-----------------+


# Predictive Parking

This is a project about the scan data analysis. Making maps of the parking "pressure"
in the city is the main goal.

The project is devided in a few docker-containers with their own functions.

  - api
     - provide web api on scan data
     - contains database building / migrations and loading of related databases
  - angluar
     - occupancy viewer build on top of api.
  - csvimporter
    - golang code which crunches to and cleans up scan data and import csv data into postgres database
  - kibana
    - default kibana to analyse scan - data. deployed at: https://acc.parkeren.data.amsterdam.nl
  - logstash
    - import data from database into elasticsearch
  - postgres
    - database docker with custom settings
  - .jenkins
    - import environment to build new dataset


There are two steps

 - 1. Prepare, combine, cleanup the data.
 - 2. Visualize the data in kibana.
 - 3. Visualize the occupancy special viewer.

https://dokuwiki.datapunt.amsterdam.nl/doku.php?id=start:pparking:architectuur


 Step 1. Preparing the data
==========================

We take data from a few sources and create a dataset usable for predictive parking analysis.

Source data:
 - all known parking spots.
 - all known roads. (wegdelen) / partial roads. (weddelen) from BGT.
 - all known neigborhoods. (buurten)
 - all 50+ milion cars scans of 2016/2017.

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


Step 3. Customized agular 4 / leaflet viewer.
==============================

After experimenting with kibana we decided to make a specialized viewer using angular4 and leaflet.
We show parking pressure for year, month, week, day by hour summaries for the parking/road map of Amsterdam.
this is a work in progres.


 TODO
=====

 - incremental data loading


Development
===========


 Step1, Data preparation:
----------------------------


  - set environment variables TESTING=no/yes (when yes will load small subset of all data),
    ENVIRONMENT=acceptance, and PARKEERVAKKEN_OBJECTSTORE password.

  - RUN .jenkins/import.sh

  - TEST .jenkins-test.sh

  - to run API test locally.

    - docker-compose up -p test database elasticsearch

    - 'cd' in the api/predictive_parking folder and run
    - bash testdata/loadtestdata.sh predictiveparking
    - bash testdata/loadelastic.sh predictiveparking
    - manage.py test will work now.

Tips.

  - Downloads are cached in named volumes. Database downloads, zips and csv's are saved.
    forcefull remove the named volume (pp_unzip-volume) if it contains the wrong data.
    When TESTING = no the `unziped` will be deleted


Step2, Visualization
----------------------------

   There is an `angular` project to visualize the data.
   See the readme / Dockerfile in the `angular` directory.

