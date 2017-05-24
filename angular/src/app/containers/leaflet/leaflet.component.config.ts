export const config = {
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
      valueProperty: 'scan_count',
        scale: ['white', 'green'],
        steps: 10,
        mode: 'q',
        style: {
          color: '#fff',
            weight: 2,
            fillOpacity: 0.8
        }
    },
    wegdelen: {
      valueProperty: 'bezetting',
      scale: ['white', 'red'],
      steps: 10,
      mode: 'q',
      style: {
        color: '#fff',
        weight: 2,
        fillOpacity: 0.8
      }
    }
  }
};
