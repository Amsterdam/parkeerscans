import { Component, AfterViewInit, ElementRef, NgZone } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import L from 'leaflet';
import 'leaflet-choropleth';
import { MapCrs } from '../../services/map-crs';
import { config } from './leaflet.component.config';
import { ParkeerkansService } from '../../services/parkeerkans';
import { WegdelenService } from '../../services/wegdelen';
import { ParkeervakkenService } from '../../services/parkeervakken';
import { Parkeerkans } from '../../models/parkeerkans';

@Component({
  selector: 'dp-leaflet',
  template: '',
  styleUrls: [
    './leaflet.scss'
  ]
})
export class LeafletComponent implements AfterViewInit {
  private leafletMap: L.Map;

  constructor(
    private host: ElementRef,
    private zone: NgZone,
    private crs: MapCrs,
    private parkeerkansService: ParkeerkansService,
    private wegdelenService: WegdelenService,
    private parkeervakkenService: ParkeervakkenService) {}

  public ngAfterViewInit() {
    this.initLeaflet();
    this.updateBoundingBox();
  }

  private initLeaflet() {
    this.zone.run(() => {
      const options = Object.assign({}, config.map, {
        crs: this.crs.getRd()
      });
      this.leafletMap = L.map(this.host.nativeElement, options)
        .setView([52.3731081, 4.8932945], 11);
      const baseLayer = L.tileLayer('https://{s}.data.amsterdam.nl/topo_rd/{z}/{x}/{y}.png', {
        subdomains: ['acc.t1', 'acc.t2', 'acc.t3', 'acc.t4'],
        tms: true,
        minZoom: 8,
        maxZoom: 16,
        bounds: config.map.maxBounds
      });

      baseLayer.addTo(this.leafletMap);

      setTimeout(() => {
        this.leafletMap.invalidateSize();
      });

      this.leafletMap.on('moveend', this.updateBoundingBox.bind(this));
      this.leafletMap.on('zoomend', this.updateBoundingBox.bind(this));
    });
  }

  private updateBoundingBox() {
    const boundingBox = this.leafletMap.getBounds().toBBoxString();
    Observable
      .zip(
        this.parkeerkansService.getParkeerkans(boundingBox, ParkeerkansService.MONDAY, 10),
        this.wegdelenService.getWegdelen(boundingBox))
      .subscribe(this.showWegdelen.bind(this), this.showError);
  }

  private showWegdelen([parkeerkans, wegdelen]: [Parkeerkans, any]) {
    const data = wegdelen.map((wegdeel) => {
      const wegdeelKans = parkeerkans.wegdelen[wegdeel.properties.id];
      wegdeel.properties.bezetting = wegdeelKans ? wegdeelKans.occupation : 0;
      return wegdeel;
    }).filter((wegdeel) => {
      return wegdeel.properties.bezetting === 'fout' ? false : wegdeel.properties.bezetting;
    });
    L.choropleth({
      type: 'FeatureCollection',
      features: data
    }, config.choropleth.wegdelen).addTo(this.leafletMap);

    const boundingBox = this.leafletMap.getBounds().toBBoxString();
    this.parkeervakkenService.getVakken(boundingBox)
      .subscribe(this.showParkeervakken.bind(this), this.showError);
  }

  private showParkeervakken(parkeervakken) {
    L.choropleth({
      type: 'FeatureCollection',
      features: parkeervakken
    }, config.choropleth.parkeervakken).addTo(this.leafletMap);
  }

  private showError(error) {
    console.error(error);
  }
}
