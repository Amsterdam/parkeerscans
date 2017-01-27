FROM kibana:5.1.2
MAINTAINER datapunt.ois@amsterdam.nl

RUN apt-get update && apt-get install -y git unzip
# COPY jVectorMapGebieden /usr/share/kibana/plugins/jVectorMapGebieden/
# RUN logstash-plugin install logstash-input-jdbc

WORKDIR /usr/share/kibana/plugins/
# RUN git clone https://github.com/Lytrix/geoJsonMapKibana.git

#RUN kibana-plugin install https://github.com/nreese/enhanced_tilemap/releases/download/v5.1.1-2016-12-14/kibana.zip

COPY jVectorMapGebieden jVectorMapGebieden
COPY enhanced_tilemap enhanced_tilemap
# COPY geoJsonMapKibana geoJsonMapKibana
