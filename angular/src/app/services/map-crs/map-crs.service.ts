import { Injectable } from '@angular/core';
import L from 'leaflet';
// Make sure the Proj4 Leaflet plugin trys to find its dependencies on the window
import 'imports-loader?define=>false,module=>false!proj4leaflet';
import { config } from './map-crs.service.config';

@Injectable()
export class MapCrs {
  private rd;

  constructor() {
    this.setRd();
  }

  public getRd() {
    return this.rd;
  }

  /*
   * @returns {Object} - An object used to identify the CRS of a GeoJSON object:
   * http://geojson.org/geojson-spec.html#coordinate-reference-system-objects
   */
  public getRdObject() {
    return {
      type: 'name',
      properties: {
        name: config.RD.code
      }
    };
  }

  private setRd() {
    const rdSettings = { ...config.RD };

    /*
     * Convert the Array syntax from the configuration to the L.bounds format
     * http://leafletjs.com/reference.html#bounds
     */
    rdSettings.transformation.bounds = L.bounds.apply(null, rdSettings.bounds);
    this.rd = new L.Proj.CRS(
      rdSettings.code,
      rdSettings.projection,
      rdSettings.transformation
    );

    /*
     * Door bug in Leaflet werkt de schaalbalk niet met de standaard RD instellingen er worden
     * voor een workaround hier 2 waarden toegevoegd. initiatie schaal in zoom.directive.js
     * https://github.com/Leaflet/Leaflet/issues/4091
     */
    this.rd.distance = L.CRS.Earth.distance;
    this.rd.R = config.EARTH_RADIUS;
  }
}
