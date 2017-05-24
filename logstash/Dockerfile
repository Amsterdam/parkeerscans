FROM logstash
MAINTAINER datapunt.ois@amsterdam.nl

RUN logstash-plugin install logstash-input-jdbc

RUN mkdir /app/

WORKDIR /app/

RUN wget https://jdbc.postgresql.org/download/postgresql-9.4.1212.jar

RUN apt-get update \
	&& apt-get install -y \
		netcat \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*



COPY readdb.conf /app/
COPY geomapping.json /app/
COPY docker-run.sh /app/
COPY load-test-data.sh /app/

# For development / testing local
# COPY tables.txt /app/data/tables.txt

CMD ["/app/docker-run.sh"]
