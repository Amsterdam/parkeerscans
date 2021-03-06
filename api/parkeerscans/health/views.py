# Python
import logging
# Packages
from django.conf import settings
from django.db import connection
from django.http import HttpResponse
from elasticsearch import Elasticsearch

from elasticsearch_dsl import Search

# Project
from metingen.models import Scan


log = logging.getLogger(__name__)


def health(_request):
    # Check Database
    try:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            assert cursor.fetchone()
    except:
        log.exception("Database connectivity failed")
        return HttpResponse(
            "Database connectivity failed",
            content_type="text/plain", status=500)

    # Check Elasticsearch
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert client.info()
    except:
        log.exception("Elasticsearch connectivity failed")
        return HttpResponse(
            "Elasticsearch connectivity failed",
            content_type="text/plain", status=500)

    # Check Debug
    if settings.DEBUG:
        log.exception("Debug mode not allowed in production")
        return HttpResponse(
            "Debug mode not allowed in production",
            content_type="text/plain", status=500)

    return HttpResponse(
        "Health OK", content_type='text/plain', status=200)


def check_data(_request):
    # Check Bag
    try:
        assert Scan.objects.count() > 2000000
    except:
        log.exception("No Scan data found")
        return HttpResponse(
            "No Scan data found",
            content_type="text/plain", status=500)

    # Check Elastic
    try:
        client = Elasticsearch(settings.ELASTIC_SEARCH_HOSTS)
        assert Search().using(client).index(
            'scans*').query("match_all", size=0)
    except:
        log.exception("elastic scans failed")
        return HttpResponse(
            "Elastic scans query failed",
            content_type="text/plain", status=500)

    return HttpResponse("Data OK", content_type='text/plain', status=200)
