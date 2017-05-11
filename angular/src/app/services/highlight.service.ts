import { Injectable } from '@angular/core';
import { MapCrs } from '../containers/map-crs.service';

const L = window.L;

@Injectable()
export class HighlightService {
  constructor(private crs: MapCrs) {}

  /**
   * @param {Object} leafletMap - A Leaflet map instance
   * @param {Object} item - An object with the following properties:
   *  - id: in case of a marker this needs to be a mapping to a key of ICON_CONFIG
   *  - geometry: GeoJSON using RD coordinates
   */
  public addMarker(leafletMap, item) {
    const color = Math.floor(item.bezetting * 255);
    console.log('color', color);
    const rgb = `rgb(${color}, 0, 0)`;
    const layer = L.Proj.geoJson(item.geometry, {
      style: () => {
        return {
          color: rgb,
          fillColor: rgb,
          weight: 2,
          opacity: 1.6,
          fillOpacity: 0.2
        };
      },
      pointToLayer: (feature, latLng) => {
        const icon = L.icon({
          iconUrl: 'assets/icons/icon-detail.svg',
          iconSize: [21, 21],
          iconAnchor: [10, 10]
        });
        const rotationAngle = item.orientation || 0;

        return L.marker(latLng, {
          icon,
          rotationAngle
        });
      }
    });
    console.log('layer', layer);

    leafletMap.addLayer(layer);
  }
}
