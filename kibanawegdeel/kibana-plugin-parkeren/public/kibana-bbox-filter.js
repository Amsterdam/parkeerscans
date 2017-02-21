import FilterBarQueryFilterProvider from 'ui/filter_bar/query_filter';

export default function (Private) {
    const queryFilter = Private(FilterBarQueryFilterProvider);
    let activeFilter = null;

    function onlyUnique(value, index, self) { 
	return self.indexOf(value) === index;
    }

    return {
        add: function (bbox) {
            const bottomRight = bbox.getSouthEast();
            const topLeft = bbox.getNorthWest();
	    
	    let corners = [
		bottomRight.lat,
		bottomRight.lng,
		topLeft.lat,
		topLeft.lng
	    ];

	    //validate corner values
	    if(corners.filter( onlyUnique ).length < 4){
		return;
	    }

            if (angular.isDefined(activeFilter)) {
                queryFilter.removeFilter(activeFilter);
            }

            activeFilter = {
                meta: {
                    index: "scans*"
                },
                "geo_bounding_box": {
                    "geo": {
                        "bottom_right": {
                            "lat": bottomRight.lat,
                            "lon": bottomRight.lng
                        },
                        "top_left": {
                            "lat": topLeft.lat,
                            "lon": topLeft.lng
                        }
                    }
                }
            };

            queryFilter.addFilters([activeFilter]);
        }
    };
}
