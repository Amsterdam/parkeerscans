module.exports = {

    MAP_OPTIONS: {
        maxBounds: [
            [52.269470, 4.72876], //southWest
            [52.4322, 5.07916] //northEast
        ],
        center: [52.379189, 4.899431],
        zoom: 13
    },

    BASE_LAYER_URL: 'https://{s}.datapunt.amsterdam.nl/topo_google/{z}/{x}/{y}.png',

    BASE_LAYER_OPTIONS: {
        minZoom: 9,
        maxZoom: 21,
        subdomains: ['t1', 't2', 't3', 't4']
    },

    VAKKEN_OPTIONS: {
        valueProperty: 'elkcount',
        scale: ['white', 'red'],
        steps: 10,
        mode: 'q', // q for quantile, e for equidistant, k for k-means
        style: {
            color: '#161', // border color
            weight: 1,
            fillOpacity: 0.5
        },

	onEachFeature: function(feature, layerv) {
	    layerv.bindPopup(
		'scans:' + feature.properties.elkcount + '<br>' +
		'type :' + feature.properties.soort
	    );
	}
    },

    //highlightFeature: function(feature, layer){

    //},

    //resetHighlight: function(feature, layer) {

    //},

    WEGDELEN_OPTIONS: {

        valueProperty: 'bezetting',

        scale: ['white','red'],
        steps: 10,
        mode: 'q', // q for quantile, e for equidistant, k for k-means
        style: {
            color: '#111', // border color
            weight: 1,
            fillOpacity: 0.3
        },

	onEachFeature: function(feature, layer) {

	    //layer.on({
	    //    mouseover: highlightFeature,
	    //    mouseout: resetHighlight,
	    //});

	    layer.bindPopup(
		    'vakken   :' + feature.properties.vakken + '<br>' +
		    'fiscaal  :' + feature.properties.fiscale_vakken + '<br>' +
		    'gezien   :' + feature.properties.vakkengezien + '<br>' +
		    'scans    :' + feature.properties.scans + '<br>' +
		    'bezetting:' + feature.properties.bezetting.toFixed(2)
	    );
	}
    }

};
