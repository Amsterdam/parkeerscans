module.exports = function(kibana) {
	return new kibana.Plugin({
		uiExports: {
			visTypes: ['plugins/jVectorMapGebieden/jvector_map_country_vis']
		}
	});
};