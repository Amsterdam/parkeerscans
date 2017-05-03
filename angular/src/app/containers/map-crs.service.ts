import { Injectable } from '@angular/core';
//import L from 'leaflet';
//import * as proj4 from 'proj4';
//import * as proj4leaflet from 'proj4leaflet';

const L = window.L;
const anyL: any = L;
//const p4: any = proj4;
//const p4l: any = proj4leaflet;

/*
declare namespace L {
  namespace Proj {
    interface CRSOptions {
      origin?: number[];
      transformation?: L.Transformation;
      scales?: number[];
      resolutions?: number[];
      bounds?: L.Bounds;
    }

    function CRS(code: string, proj4def: string, options: CRSOptions): L.CRS;
  }
}
*/


const config = {
  RD: {
    code: 'EPSG:28992',
    projection: '+proj=sterea +lat_0=52.15616055555555 +lon_0=5.38763888888889 +k=0.9999079 +x_0=155000 +' +
    'y_0=463000 +ellps=bessel +units=m +towgs84=565.2369,50.0087,465.658,-0.406857330322398,0.3507326' +
    '76542563,-1.8703473836068,4.0812 +no_defs',
    transformation: {
      resolutions: [
        3440.640, 1720.320, 860.160, 430.080, 215.040, 107.520, 53.760, 26.880, 13.440, 6.720, 3.360,
        1.680, 0.840, 0.420, 0.210, 0.105, 0.0525
      ],
      bounds: [
        [-285401.92, 22598.08],
        [595301.9199999999, 903301.9199999999]
      ],
      origin: [-285401.92, 22598.08]
    }
  },
  WGS84: {
    code: 'EPSG:4326',
    projection: '+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs'
  },
  EARTH_RADIUS: 6378137 // The radius in meters
}

@Injectable()
export class MapCrs {
  private rd;

  constructor() {
    this.setRd();
  }

  private setRd() {
    const rdSettings = { ...config.RD };

    /*
     * Convert the Array syntax from the configuration to the L.bounds format
     * http://leafletjs.com/reference.html#bounds
     */
    rdSettings.transformation.bounds = L.bounds.apply(null, rdSettings.transformation.bounds);
    this.rd = new anyL.Proj.CRS(
      rdSettings.code,
      rdSettings.projection,
      rdSettings.transformation
    );

    /*
     * Door bug in Leaflet werkt de schaalbalk niet met de standaard RD instellingen er worden
     * voor een workaround hier 2 waarden toegevoegd. initiatie schaal in zoom.directive.js
     * https://github.com/Leaflet/Leaflet/issues/4091
     */
    //this.rd.distance = L.CRS.Earth.distance;
    //this.rd.R = config.EARTH_RADIUS;
  }

  public getRd () {
    return this.rd;
  }

  /*
   * @returns {Object} - An object used to identify the CRS of a GeoJSON object:
   * http://geojson.org/geojson-spec.html#coordinate-reference-system-objects
   */
  public getRdObject () {
    return {
      type: 'name',
      properties: {
        name: config.RD.code
      }
    };
  }
}
