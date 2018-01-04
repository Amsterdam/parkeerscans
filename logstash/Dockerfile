FROM docker.elastic.co/logstash/logstash-oss:6.1.1
MAINTAINER datapunt.ois@amsterdam.nl

RUN logstash-plugin install logstash-input-jdbc

USER root
RUN mkdir /app/

WORKDIR /app/

RUN yum install nmap-ncat -y

RUN curl -O https://jdbc.postgresql.org/download/postgresql-9.4.1212.jar

COPY readdb.conf /app/
COPY geomapping.json /app/
COPY docker-run.sh /app/
COPY load-test-data.sh /app/

# UNCOMMENT For development / testing local
# COPY /app/data/tables.txt /app/data/tables.txt

USER logstash
CMD ["/app/docker-run.sh"]
