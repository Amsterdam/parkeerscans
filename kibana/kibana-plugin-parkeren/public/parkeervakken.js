define(function (require) {
    require('plugins/kibana-plugin-parkeren/lib/jquery-3.1.1');
    require('plugins/kibana-plugin-parkeren/lib/leaflet');
    require('plugins/kibana-plugin-parkeren/lib/choropleth');


    require('plugins/kibana-plugin-parkeren/parkeervakken.controller');

    function ParkeervakkenProvider (Private, getAppState, courier, config) {
        const TemplateVisType = Private(require('ui/template_vis_type/template_vis_type'));
        const Schemas = Private(require('ui/vis/schemas'));

        return new TemplateVisType({
            name: 'trParkeervakken',
            title: 'Parkeervakken',
            icon: 'fa-map',
            description: '',
            requiresSearch: true,
            template: require('plugins/kibana-plugin-parkeren/parkeervakken.html'),
            schemas: new Schemas([
		{
                    group: 'buckets',
                    name: 'wegdelen',
                    title: 'Wegdelen',
                    min: 1,
                    max: 200,
                    aggFilter: '!geohash_grid'
                },

		{
                    group: 'buckets',
                    name: 'vakken',
                    title: 'vakken',
                    min: 1,
                    max: 1,
                    aggFilter: '!geohash_grid'
                },
            ])
        });
    }

    require('ui/registry/vis_types').register(ParkeervakkenProvider);

    return ParkeervakkenProvider;
});
