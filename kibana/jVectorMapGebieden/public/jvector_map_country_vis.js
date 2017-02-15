// Include the angular controller
require('plugins/jVectorMapGebieden/jvector_map_country_visController');
require('plugins/jVectorMapGebieden/jquery-jvectormap-2.0.3.min');
require('plugins/jVectorMapGebieden/jquery-jvectormap-buurt-mill');
require('plugins/jVectorMapGebieden/jquery-jvectormap-2.0.3.css');

// The provider function, which must return our new visualization type
function jVectorMapGebiedenProvider(Private) {
	var TemplateVisType = Private(require('ui/template_vis_type/template_vis_type'));
	// Include the Schemas class, which will be used to define schemas
	var Schemas = Private(require('ui/vis/schemas'));

	// Describe our visualization
	return new TemplateVisType({
		name: 'jVectorMapGebieden', // The internal id of the visualization (must be unique)
		title: 'Gebieden kaart', // The title of the visualization, shown to the user
		description: 'Gebieden kaart van de Gemeente Amsterdam met jVectorMap.', // The description of this vis
		icon: 'fa-map', // The font awesome icon of this visualization
		template: require('plugins/jVectorMapGebieden/jvector_map_country_vis.html'), // The template, that will be rendered for this visualization
		params: {
			editor: require('plugins/jVectorMapGebieden/jvector_map_country_vis_editor.html'), // Use this HTML as an options editor for this vis
			defaults: { // Set default values for paramters (that can be configured in the editor)
				mapBackgroundColor:"#C0C0FF",countryColorMin:"#00FF00",countryColorMax:"#FF0000"
				,selectedMap:'buurt',maps:['buurt'],normalizeInput:false
			}
		},
		// Define the aggregation your visualization accepts
		schemas: new Schemas([
				{
					group: 'metrics',
					name: 'buurtvalue',
					title: 'Buurt waarde',
					min: 1,
					max: 1,
					aggFilter: ['count', 'avg', 'sum', 'min', 'max', 'cardinality', 'std_dev']
				},
				{
					group: 'buckets',
					name: 'buurt',
					title: 'Buurtcode',
					min: 1,
					max: 1,
					aggFilter: '!geohash_grid'
				},

				//{
				//	group: 'buckets',
				//	name: 'dagen',
				//	title: 'Dagen',
				//	min: 1,
				//	max: 1,
				//	aggFilter: 'date_histogram',
                //    field: '@timestamp',
                //    interval: "day"
				//}
			])
	});
}

require('ui/registry/vis_types').register(jVectorMapGebiedenProvider);
