import { Directive, ElementRef, Input, NgZone } from '@angular/core';
//import L from 'leaflet';
import { MapCrs } from './map-crs.service';

const L = window.L;

const mapOptions = {
  maxBounds: [
    [52.269470, 4.72876],
    [52.4322, 5.07916]
  ],
  // 1.0 makes the bounds fully solid, preventing the user from dragging outside the bounds
  maxBoundsViscosity: 1.0,
  bounceAtZoomLimits: false,
  attributionControl: false,
  zoomControl: false
}

@Directive({ selector: '[dp-leaflet]' })
export class LeafletDirective {
  constructor(el: ElementRef, zone: NgZone, private crs: MapCrs) {
    zone.run(() => {
      const options = Object.assign({}, mapOptions, {
        crs: this.crs.getRd()
      });
      console.log('crs', options);
      const leafletMap: L.Map = L.map(el.nativeElement, options)
        .setView([52.3731081, 4.8932945], 11);
      const baseLayer = L.tileLayer('https://{s}.data.amsterdam.nl/topo_rd/{z}/{x}/{y}.png', {
        subdomains: ['acc.t1', 'acc.t2', 'acc.t3', 'acc.t4'],
        tms: true,
        minZoom: 8,
        maxZoom: 16,
        bounds: mapOptions.maxBounds
      });

      baseLayer.addTo(leafletMap);

      setTimeout(() => {
        leafletMap.invalidateSize();
      });
    });
  }
}
