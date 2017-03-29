const module = require('ui/modules').get('parkeervakken');
const PLUGIN_CONFIG = require('./parkeervakken-config');

module.controller('ParkeervakkenController', function ($scope, $http, Private) {
    const geofilterManager = require('./kibana-bbox-filter')(Private);

    let map,
        baseLayer,
        legend,
        wegdelenLayer,
        vakkenMap,
        wegMap,
        vakkenLayer;

    $scope.$watch('esResponse', (esData) => {
        if (angular.isUndefined(map)) {
            initializeMap();
        }

        if (angular.isDefined(esData)) {

        //console.log(map.getZoom());
        if (map.getZoom() < 16) {
            return;
        }

        parseEsData(esData);

        fetchWfsWegdelen().then((wfsWegData) => {
            fetchWfsParkeervakken().then((wfsVakData) => {
                drawWegDelen(wfsWegData);
                drawVakken(wfsVakData);
            });
        });

        }

    });

    function initializeMap () {
        map = L.map(document.querySelector('.js-leaflet-map'), PLUGIN_CONFIG.MAP_OPTIONS);
        baseLayer = L.tileLayer(PLUGIN_CONFIG.BASE_LAYER_URL, PLUGIN_CONFIG.BASE_LAYER_OPTIONS);
        map.addLayer(baseLayer);

        map.on('moveend', updateBoundingBox);
        map.on('zoomend', updateBoundingBox);
        //updateBoundingBox();
    }

    /**
     * Communicate the new boudingbox to Kibana
     */

    function updateBoundingBox () {
        geofilterManager.add(map.getBounds());
    }

    function parseEsData (esData) {
        if (angular.isUndefined(esData)) {
            return;
        }

        const wegId = $scope.vis.aggs.bySchemaName['wegdelen'][0].id;
        const wegBuckets = esData.aggregations[wegId].buckets;

    vakkenMap = {};
    wegMap = {};

    wegBuckets.forEach(wegdeel => {

       const key = wegdeel.key;

       let vakken = 0;

       if(wegdeel['1-orderAgg'] !== undefined){
        vakken = wegdeel['1-orderAgg'].value;
       }

       wegMap[wegdeel.key] = {
        'scans': wegdeel.doc_count,
        'vakkengezien': vakken || 0
       };

       if(wegdeel[2].buckets !== undefined){
           wegdeel[2].buckets.forEach( vak => {
               vakkenMap[vak.key] = vak.doc_count;
           });
       }
    });
    }


    function fetchWfsParkeervakken () {
        const BBOX = map.getBounds().toBBoxString();
        const WFS_URL = 'https://map-acc.data.amsterdam.nl/maps/parkeervakken?' +
            'REQUEST=Getfeature&' +
            'VERSION=1.1.0&' +
            'SERVICE=wfs&' +
            'TYPENAME=alle_parkeervakken&' +
            'srsName=EPSG:4326&' +
            'count=4000&' +
            'startindex=0&' +
            'outputformat=geojson&' +
            'bbox=' + BBOX;

        return $http.get(WFS_URL).then(response => response.data);
    }

    function fetchWfsWegdelen () {
        const BBOX = map.getBounds().toBBoxString();
        const WFS_URL = 'https://map-acc.data.amsterdam.nl/maps/predictiveparking?' +
            'REQUEST=Getfeature&' +
            'VERSION=1.1.0&' +
            'SERVICE=wfs&' +
            'TYPENAME=wegdelen&' +
            'srsName=EPSG:4326&' +
            'count=1500&' +
            'startindex=0&' +
            'outputformat=geojson&' +
            'bbox=' + BBOX;

        return $http.get(WFS_URL).then(response => response.data);
    }

    function wegDelenLegend(div) {
	if( wegdelenLayer !== undefined) {

            let limits = wegdelenLayer.options.limits;
            let colors = wegdelenLayer.options.colors;

            // Add min & max
            div.innerHTML += '<div class="labels"><div class="min">' + limits[0] + '</div>'+
                '<div class="type"> wegdelen </div><div class="max">' + limits[limits.length - 1] + '</div></div>';

            let labels2 = [];

            limits.forEach(function (limit, index) {
              labels2.push(
                '<li style="background-color: ' +
                 colors[index] + '"></li>');
            });

            div.innerHTML += '<ul>' + labels2.join('') + '</ul>';

	}
    }

    function addLegend() {

      // remove old legend if present
      if(legend !== undefined) {
        legend.remove(map);
        legend = undefined;
      }

      legend = L.control({ position: 'bottomright' });

      legend.onAdd = function (map) {
          let div = L.DomUtil.create('div', 'legend');
          let limits = vakkenLayer.options.limits;
          let colors = vakkenLayer.options.colors;

          // Add min & max
          div.innerHTML = '<div class="labels"><div class="min">' + limits[0] + '</div>'+
              '<div class="type"> scans </div><div class="max">' + limits[limits.length - 1] + '</div></div>';

          let labels = [];
          limits.forEach(function (limit, index) {
            labels.push(
              '<li style="background-color: ' +
               colors[index] + '"></li>');
          });

          div.innerHTML += '<ul>' + labels.join('') + '</ul>';

	  //add wegdelen layer
	  wegDelenLegend(div);

          return div;
      };

      legend.addTo(map);
    }

    function drawWegDelen(wfsData){
        // Clean up old data shown by the plugin before adding new data
        if (map.hasLayer(wegdelenLayer)) {
            wegdelenLayer.clearLayers();
            map.removeLayer(wegdelenLayer);
        }

        wfsData.features = wfsData.features.filter(function(feature){
            let p = feature.properties;
            return(p.vakken !== "");
        });

        wfsData.features = wfsData.features.map(feature => {
            const wegId = feature.properties.id;
            const wegDeel = wegMap[wegId];


            let p = feature.properties;

            if (wegDeel) {
                p.vakkengezien = wegDeel.vakkengezien;
                let beschikbaar = p.vakken || 0;
                p.scans = wegDeel.scans;
                let bezetting = p.vakkengezien / p.fiscale_vakken * 100;
                if( bezetting > 100) {
                  bezetting = 100;
                }
                p.bezetting = bezetting;
            } else {
                p.vakkengezien = 0;
                p.scans = 0;
                p.bezetting = 0;
            }

            return feature;
        });

        // Show the new data
        wegdelenLayer = L.choropleth(wfsData, copy(PLUGIN_CONFIG.WEGDELEN_OPTIONS));
        map.addLayer(wegdelenLayer);
    }

    function drawVakken (wfsData) {
        // Loop through all parkeervakken
        wfsData.features = wfsData.features.map(feature => {
            const parkeervakId = feature.properties.id;
        const hasMatch = vakkenMap[parkeervakId];

            if (hasMatch) {
                feature.properties.elkcount = hasMatch;
            } else {
                feature.properties.elkcount = 0;
            }

            return feature;
        });

        // Clean up old data shown by the plugin before adding new data
        if (map.hasLayer(vakkenLayer)) {
            vakkenLayer.clearLayers();
            map.removeLayer(vakkenLayer);
        }

        // Show the new data
        vakkenLayer = L.choropleth(wfsData, copy(PLUGIN_CONFIG.VAKKEN_OPTIONS));
        map.addLayer(vakkenLayer);
        addLegend();
    }

    function copy (input) {
        return jQuery.extend(true, {}, input);
    }

});
