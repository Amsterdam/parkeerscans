FROM amsterdam/python
MAINTAINER datapunt@amsterdam.nl

ENV PYTHONUNBUFFERED 1

RUN apt-get install -y \
	unar \
	&& apt-get clean


RUN adduser --system datapunt \
	&& mkdir -p /static \
	&& chown datapunt /static \
	&& mkdir -p /app/unzipped \
	&& chown datapunt /app/unzipped \
	&& mkdir -p /app/data \
	&& chown datapunt /app/data \
	&& pip install uwsgi

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

USER datapunt

COPY predictive_parking /app/

CMD ["/app/docker-run.sh"]
