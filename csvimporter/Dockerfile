FROM golang:latest
MAINTAINER datapunt.ois@amsterdam.nl


COPY . src/app

WORKDIR /go/src/app

RUN go get
RUN go build
