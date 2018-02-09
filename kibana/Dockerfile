FROM docker.elastic.co/kibana/kibana-oss:6.1.1
MAINTAINER datapunt.ois@amsterdam.nl

USER root
RUN yum install -y git unzip

WORKDIR /usr/share/kibana/plugins/

# COPY jVectorMapGebieden jVectorMapGebieden
# COPY enhanced_tilemap enhanced_tilemap
# COPY kibana-plugin-parkeren kibana-plugin-parkeren

USER kibana
