import { Component, AfterViewInit, ElementRef, NgZone } from '@angular/core';
import L from 'leaflet';
import { MapCrs } from '../../services/map-crs';
import { config } from './leaflet.component.config';

@Component({
  selector: 'dp-leaflet',
  template: '',
  styleUrls: [
    './leaflet.scss'
  ]
})
export class LeafletComponent implements AfterViewInit {
  constructor(private host: ElementRef, private zone: NgZone, private crs: MapCrs) {
  }

  public ngAfterViewInit() {
    this.zone.run(() => {
      const options = Object.assign({}, config, {
        crs: this.crs.getRd()
      });
      const leafletMap: L.Map = L.map(this.host.nativeElement, options)
        .setView([52.3731081, 4.8932945], 11);
      const baseLayer = L.tileLayer('https://{s}.data.amsterdam.nl/topo_rd/{z}/{x}/{y}.png', {
        subdomains: ['acc.t1', 'acc.t2', 'acc.t3', 'acc.t4'],
        tms: true,
        minZoom: 8,
        maxZoom: 16,
        bounds: config.maxBounds
      });

      baseLayer.addTo(leafletMap);

      setTimeout(() => {
        leafletMap.invalidateSize();
      });
    });
  }
}
