FROM kibana:5.2.1
MAINTAINER datapunt.ois@amsterdam.nl

RUN apt-get update && apt-get install -y git unzip

WORKDIR /usr/share/kibana/plugins/

COPY jVectorMapGebieden jVectorMapGebieden
COPY enhanced_tilemap enhanced_tilemap
# COPY kibana-plugin-parkeren kibana-plugin-parkeren
