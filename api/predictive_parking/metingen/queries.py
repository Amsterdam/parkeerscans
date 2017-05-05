"""
ELasticseach queries
"""

from elasticsearch_dsl import Search
from elasticsearch_dsl import A


class ElasticQueryWrapper(object):
    """
    Wrapper object for dynamically constructing elastic search queries.
    """

    def __init__(
            self, query,
            indexes: [str] = None,
            aggs=[],
            size: int = None):
        """
        :param query: an elastic search query
        :param sort_fields: an optional list of fields
            to use for server-side sorting
        :param indexes: an optional list of indexes to use

        :param size: an optional limit on size of
            the result set
        """
        self.query = query
        self.indexes = indexes
        self.size = size
        self.aggs = aggs

    def to_elasticsearch_object(self, client) -> Search:
        assert self.indexes

        search = (
            Search()
            .using(client)
            .index(*self.indexes)
            .query(self.query)
        )

        # sample size
        size = 2  # default size

        if self.size:
            size = self.size

        search = search[0:size]

        return search


def aggregation_query(
        bbox=[]
        # must: [dict] = None,
        # must_not: [dict] = None
        ):
    """
    Crate aggregation query
    """
    assert bbox

    elk_q = ElasticQueryWrapper(
        query={'match_all': {}},
        indexes=["scans-*", ]
    )

    return elk_q


def build_bbox(bbox):
    """
    build bbox part of query
    """

    lat, lon, lat1, lon1 = bbox

    bbox_q = """

    """

    return bbox_q


def build_wegdeel_query(_bbox, query="", ):
    """

    Build aggregation determine distinct vakken for each wegdeel
    per day.

    """


    wegdeel_agg = """
    {
        %s
        "aggs": {
            "scan_by_date": {
                "date_histogram": {
                    "field": "@timestamp",
                    "interval": "1d",
                    "format": "yyyy-MM-dd",
                    "keyed": true
                 },
                 "aggs": {
                    "wegdeel": {
                        "terms": {
                            "field": "bgt_wegdeel.keyword",
                            "size": 90
                        },
                        "aggs": {
                            "vakken": {
                                "cardinality": {
                                    "field": "parkeervak_id.keyword"
                                }
                            }
                        }
                    }
                 }

             }
        }
    }
    """ % (query)

    return wegdeel_agg
