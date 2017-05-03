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
