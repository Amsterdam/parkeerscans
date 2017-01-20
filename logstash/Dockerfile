FROM logstash
MAINTAINER datapunt.ois@amsterdam.nl

RUN logstash-plugin install logstash-input-jdbc

RUN mkdir /app/

WORKDIR /app/
RUN wget https://jdbc.postgresql.org/download/postgresql-9.4.1212.jar

# USER datapunt

COPY readdb.conf /app/
COPY geomapping.json /app/
COPY docker-run.sh /app/

CMD ["/app/docker-run.sh"]
