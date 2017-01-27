# jVectorMapGebieden

A jVectormap of the Neighborhoods of the City of Amsterdam for Kibana 5.1.1.

Simply unzip the content in the plugin folder of Kibana. The aggregation key must match the neighborhood code as defined for the City of Amsterdam neighborhoods which can be found in the <a href="https://api.datapunt.amsterdam.nl/gebieden/buurt/">API Gebieden</a> in the display name or in each URI named: vollcode for example: Kop Zeedijk = A00a.

The "Normalize Input To UpperCase" simply aggregates lower and upper case values together. For example a record set with "us":2 and "US":1 becomes "US":3.

Maps are obtained via this webservice: https://map.datapunt.amsterdam.nl/maps/gebieden?REQUEST=GetCapabilities&SERVICE=wfs"

The plugin is a Fork of this Kibana plugin: https://github.com/snuids/Elastic-5.0-Country-Map-Visualizer
Screenshots here: https://github.com/snuids/jVectorMapKibanaCountry/wiki
