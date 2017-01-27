FROM kibana:5.1.2
MAINTAINER datapunt.ois@amsterdam.nl

RUN apt-get update && apt-get install -y git unzip

WORKDIR /usr/share/kibana/plugins/

#RUN kibana-plugin install https://github.com/nreese/enhanced_tilemap/releases/download/v5.1.1-2016-12-14/kibana.zip

COPY jVectorMapGebieden jVectorMapGebieden
COPY enhanced_tilemap enhanced_tilemap
# COPY geoJsonMapKibana geoJsonMapKibana
