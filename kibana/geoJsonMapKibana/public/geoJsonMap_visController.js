// Create an Angular module for this plugin
var module = require('ui/modules').get('geojsonmap_vis');


module.controller('geoJsonMapController', function($scope, Private) {

	var filterManager = Private(require('ui/filter_manager'));

	$scope.filter = function(tag) {
		// Add a new filter via the filter manager
		filterManager.add(
			// The field to filter for, we can get it from the config
			$scope.vis.aggs.bySchemaName['locations'][0].params.field,
			// The value to filter for, we will read out the bucket key from the tag
			location.label,
			// Whether the filter is negated. If you want to create a negated filter pass '-' here
			null,
			// The index pattern for the filter
			$scope.vis.indexPattern.title
		);
	};

	$scope.$watch('esResponse', function(resp) {
		if (!resp) {
			$scope.locations = null;
			return;
		}

		if($scope.vis.aggs.bySchemaName['countries']=== undefined)
		{
			$scope.locations = null;
			return;
		}

		// Retrieve the id of the configured tags aggregation
		var locationsAggId = $scope.vis.aggs.bySchemaName['countries'][0].id;
		// Retrieve the metrics aggregation configured
		var metricsAgg = $scope.vis.aggs.bySchemaName['countryvalue'][0];
		var buckets = resp.aggregations[locationsAggId].buckets;


		// Transform all buckets into tag objects
		$scope.locations = buckets.map(function(bucket) {
			// Use the getValue function of the aggregation to get the value of a bucket
			var key = bucket.key;
			var value = metricsAgg.getValue(bucket);
			// REMOVE substring to get origional vollcode 'A00a'. It is now used to join on '00a'.
			// var key = key.substring(1, 4);
			return {
				key : key,
				value : value
			};

		});

		//console.log($scope.locations);

		// Draw Map

		try { $('#map').map.remove(); }
		catch(err) {}

		var data={};

		angular.forEach($scope.locations, function(test){
			//if(value.label!=undefined)
			data[test.key]=test.value;
		});


		console.log(data);

		//var geoJsonURL = 'https://map.datapunt.amsterdam.nl/maps/gebieden';
		var geoJsonURL = 'https://map.datapunt.amsterdam.nl/maps/parkeervakken';
		var geoJsonURL = $scope.vis.params.geoJsonURL
		//var typeName = 'buurt';
		var typeName = $scope.vis.params.typeName;
		var start_at_zoom = $scope.vis.params.zoomLimitLevel;
		var choroplethLayer;
		//TODO add editor string "code" value to parameter field as code
		var geoJsonIdField = $scope.vis.params.geoJsonIdField;
		var toolTip;

		var map = L.map('map', {
	                      maxBounds: [
	                          [52.269470, 4.72876], //southWest
	                          [52.4322, 5.07916] //northEast
	                      ]
	                  })
	                  .setView([52.379189, 4.899431], 11);


		// Add basemap
		var baseLayerOptions = {
		                  minZoom: 11,
		                  maxZoom: 21,
		                  subdomains: ['t1', 't2', 't3', 't4'],
		                  attribution: '&copy; <a href="http://api.datapunt.amsterdam.nl">Datapunt</a>',
		                  fadeAnimation: false
		              };

		var baseLayers = { 'Topografie': L.tileLayer($scope.vis.params.baseLayerUrl, baseLayerOptions),
						   'Luchtfoto': L.tileLayer.wms('https://map.datapunt.amsterdam.nl/maps/lufo',
						   	{ layers: 'lufo2016',
                                format: 'image/png',
                                transparent: false
                                })
                           };
		var overlays = {
              "Stadsdelen": L.tileLayer.wms('https://map.datapunt.amsterdam.nl/maps/gebieden', 
                              { layers: 'stadsdeel,stadsdeel_label',
                                format: 'image/png',
                                transparent: true
                                }),
              "Gebieden":   L.tileLayer.wms('https://map.datapunt.amsterdam.nl/maps/gebieden', 
                              { layers: 'gebiedsgerichtwerken,gebiedsgerichtwerken_label',
                                format: 'image/png',
                                transparent: true
                                }),
              "Wijken":     L.tileLayer.wms('https://map.datapunt.amsterdam.nl/maps/gebieden', 
                              { layers: 'buurtcombinatie,buurtcombinatie_label',
                                format: 'image/png',
                                transparent: true
                                }),
              "Buurten":    L.tileLayer.wms('https://map.datapunt.amsterdam.nl/maps/gebieden', 
                              { layers: 'buurt,buurt_label',
                                format: 'image/png',
                                transparent: true
                                })
              };             
  		
  		//Load control layers 
    	L.control.layers(baseLayers,overlays).addTo(map); 
    	// Load default baselayer
    	baseLayers['Topografie'].addTo(map);
    	// Load default overlay
    	overlays['Buurten'].addTo(map);


		// Add GeoJSON

	
		function onEachFeature(feature, layer) {
		    // does this feature have a property named id?
		    if (feature.properties && feature.properties[geoJsonIdField]) {
		        toolTip = '<b>'+feature.properties[geoJsonIdField]+'</b>: '+feature.properties.value.toString();
		        //console.log(toolTip);
		        layer.bindTooltip(toolTip);
		        //layer.bindPopup(toolTip);
		    }
		    // If name property:
		     if (feature.properties && feature.properties.naam) {
		        toolTip = '<b>'+feature.properties.naam+'</b>: '+feature.properties.value.toString();
		        //console.log(toolTip);
		        layer.bindTooltip(toolTip);
		        //layer.bindPopup(toolTip);
		    }

		    	    // If name property:
		     if (feature.properties && feature.properties.naam && feature.properties[geoJsonIdField]) {
		        toolTip = '<b>'+feature.properties.naam+'</b> ('+feature.properties[geoJsonIdField]+'): '+feature.properties.value.toString();
		        //console.log(toolTip);
		        layer.bindTooltip(toolTip);
		        //layer.bindPopup(toolTip);
		    }
		    layer.on("mouseover", function (e) {		
  					var layer = e.target;
			    	layer.setStyle(highLightPolygon);
  				});
		    layer.on("mouseout", function (e) {		
  					var layer = e.target;
			    	layer.setStyle(defaultPolygon);
  				});
		}

		var defaultPolygon = {
					       color: $scope.vis.params.strokeColor,
					      weight: $scope.vis.params.strokeWidth,
			         fillOpacity: 0.7
					 };

		var highLightPolygon = {
				        weight: 3,
				        color: '#666',
				        dashArray: '',
				        fillOpacity: 0.7
				    	};

		// Add legend (don't forget to add the CSS from index.html)
		function addLegend() {

			var legend = L.control({ position: 'bottomright' });
			legend.onAdd = function (map) {
			    var div = L.DomUtil.create('div', 'info legend');
			    var limits = choroplethLayer.options.limits;
			    var colors = choroplethLayer.options.colors;
			    var labels = [];

			    // Add min & max
			    div.innerHTML = '<div class="labels"><div class="min">' + limits[0] + '</div>'+
			    				'<div class="max">' + limits[limits.length - 1] + '</div></div>';

			    limits.forEach(function (limit, index) {
			      	labels.push('<li style="background-color: ' + colors[index] + '"></li>');
			    	});

			    div.innerHTML += '<ul>' + labels.join('') + '</ul>';
			   
			    return div;
			};

		  	legend.addTo(map);
			
		 }	

		function wfsQuery() {
			var geoJsonURL = $scope.vis.params.geoJsonURL;
	        var defaultParameters = {
	            service: 'WFS',
	            version: '1.1.0',
	            request: 'getFeature',
	            typeName: $scope.vis.params.typeName,
	            maxFeatures: 3000,
	            outputFormat: 'geoJson',
	            srsName: 'EPSG:4326'
			};

		    var customParams = {
		        bbox: map.getBounds().toBBoxString()
	      		};
	        var parameters = L.Util.extend(defaultParameters, customParams);
	        console.log(geoJsonURL + L.Util.getParamString(parameters));

	        $.ajax({
	            jsonp: false,
	            url: geoJsonURL + L.Util.getParamString(parameters),
	            //dataType: 'jsonp',
	            //jsonpCallback: 'getJson',
	            success: loadGeoJson
	       		});
			}

		function load_wfs() {
		    if (map.getZoom() > start_at_zoom && $scope.vis.params.zoomLimit === true) {
		    	try { choroplethLayer.clearLayers();
		    		  $( ".legend" ).remove();
		    	}
		    	catch (e) {}
		        wfsQuery();
		    } else if ($scope.vis.params.zoomLimit === false){
		    	try { choroplethLayer.clearLayers();
		    		  $( ".legend" ).remove();
		    	}
		    	catch (e) {}
		        wfsQuery();
		    } else {
		        alert("please zoom in to see the polygons!");
		    	try { choroplethLayer.clearLayers();}
		    	catch (e) {}
		    	}
			}

		function loadGeoJson(dataGeoJson) {
		    //console.log(dataGeoJson);
		    //console.log(data);
		    $("#total").html(dataGeoJson.features.length);
		    //choroplethLayer.clearLayers();
		 
			$.when(
			    	data,
			    	dataGeoJson
			    	//$.getJSON(geoJsonURL)
				).done(function (a, b) {
				    // First get the two objects from json
				    var returnValues = a;
				    //console.log(returnValues);
				    
				    var returnGeoJson = b;
			    	console.log(returnValues);
			    	console.log(returnGeoJson);
			    	// Add value from hash table to geojson properties
			    	returnGeoJson.features.forEach(function (item) {
			    		// Add item value to array of geojson by getting returnValues['02a'] for example which matches returnValue 02a: 833
			      		item.properties.value = returnValues[item.properties[geoJsonIdField]] || 0;
			    	});
			    	console.log('added values: ' + returnGeoJson);
 					
				    //choroplethLayer.addData(returnGeoJson);
				    //addLegend();
				   	
				   	choroplethLayer = L.choropleth(
					returnGeoJson, {
					valueProperty: 'value',
					//scale: ['#00A03C','#5ABD00','#B4E600','#FFF498','#F6B400','#FF9100','#FF0000'],
					scale:[$scope.vis.params.colorMin, $scope.vis.params.colorMax],
					steps: $scope.vis.params.colorSteps,
					mode: 'k',
					style: defaultPolygon,
					onEachFeature: onEachFeature
				}).addTo(map);	
				addLegend();
		
				   	//drawGeoJson(returnGeoJson);

				});
		}


		map.on('moveend', load_wfs);

	
	});
});
