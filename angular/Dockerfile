FROM node:6.10

MAINTAINER datapunt.ois@amsterdam.nl

EXPOSE 80


RUN apt-get update \
 && apt-get install -y git nginx build-essential openjdk-7-jre \
 && apt-get clean \
 && mkdir /app

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64

WORKDIR /app
COPY *.json /app/

RUN rm -rf node_modules\
 && yarn install

COPY . /app/

ARG BUILD_ID
ENV BUILD_ID=$BUILD_ID

#RUN grunt set-build-id --buildid=${BUILD_ID}

RUN yarn run build:prod \
 && cp -r /app/dist/. /var/www/html/

COPY default.conf /etc/nginx/conf.d/
RUN rm /etc/nginx/sites-enabled/default

# forward request and error logs to docker log collector
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
	&& ln -sf /dev/stderr /var/log/nginx/error.log

CMD ["nginx", "-g", "daemon off;"]
