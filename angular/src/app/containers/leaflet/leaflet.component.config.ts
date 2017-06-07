export const config: {
  map: {
    maxBounds: Array<[number, number]>;
    maxBoundsViscosity: number;
    bounceAtZoomLimits: boolean;
    attributionControl: boolean;
    zoomControl: boolean;
  };
  choropleth: any;
} = {
  map: {
    maxBounds: [
      [52.269470, 4.72876],
      [52.4322, 5.07916]
    ],
    // 1.0 makes the bounds fully solid, preventing the user from dragging outside the bounds
    maxBoundsViscosity: 1.0,
    bounceAtZoomLimits: false,
    attributionControl: false,
    zoomControl: false
  },
  choropleth: {
    parkeervakken: {
      valueProperty: 'bezetting',
        scale: ['white', 'red'],
        steps: 11,
        mode: 'q',
        style: {
          color: '#fff',
          weight: 1,
          fillOpacity: 0.6
        }
    },
    wegdelen: {
      valueProperty: 'bezetting',
      scale: ['white', 'red'],
      steps: 11,
      mode: 'q',
      style: {
        color: '#fff',
        weight: 0,
        fillOpacity: 0.6
      },
      onEachFeature: function(feature, layer) {
	layer.bindPopup(feature.properties.bezetting.toFixed(2) + '% van ' + feature.properties.vakken + 'vakken')
      }
    }
  }
};
