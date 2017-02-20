FROM kibana:5.2.1
MAINTAINER datapunt.ois@amsterdam.nl

RUN apt-get update && apt-get install -y git unzip

WORKDIR /usr/share/kibana/plugins/

# RUN kibana-plugin install https://github.com/nreese/enhanced_tilemap/releases/download/v5.1.1-2016-12-14/kibana.zip

COPY jVectorMapGebieden jVectorMapGebieden
# COPY enhanced_tilemap enhanced_tilemap
COPY kibana-plugin-parkeren kibana-plugin-parkeren
# COPY parkeren parkeren

# COPY geoJsonMapKibana geoJsonMapKibana
