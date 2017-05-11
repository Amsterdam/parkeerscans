// import L from 'leaflet';
import 'rxjs/add/operator/map';
import { Directive, OnInit, ElementRef, Input, NgZone } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { MapCrs } from './map-crs.service';
import { ParkeerkansService } from '../services/parkeerkans.service';
import { WegdelenService } from '../services/wegdelen.service';
import { HighlightService } from '../services/highlight.service';

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
};

@Directive({ selector: '[dp-leaflet]' })
export class LeafletDirective implements OnInit {
  private leafletMap: L.Map;
  private parkeerkans;

  constructor(
    private el: ElementRef,
    private zone: NgZone,
    private crs: MapCrs,
    private parkeerkansService: ParkeerkansService,
    private wegdelenService: WegdelenService,
    private highlightService: HighlightService) {}

  public ngOnInit() {
    this.initLeaflet();
    this.initLayer();
  }

  private initLeaflet() {
    const options = Object.assign({}, mapOptions, {
      crs: this.crs.getRd()
    });
    this.leafletMap = L.map(this.el.nativeElement, options)
      .setView([52.3625052, 4.9080058], 13);
    const baseLayer = L.tileLayer('https://{s}.data.amsterdam.nl/topo_rd_zw/{z}/{x}/{y}.png', {
      subdomains: ['acc.t1', 'acc.t2', 'acc.t3', 'acc.t4'],
      tms: true,
      minZoom: 8,
      maxZoom: 16,
      bounds: mapOptions.maxBounds
    });

    baseLayer.addTo(this.leafletMap);

    setTimeout(() => {
      this.leafletMap.invalidateSize();
    });
  }

  private initLayer() {
    const boundingBox = this.leafletMap.getBounds().toBBoxString();
    Observable
      .zip(
        this.parkeerkansService.getParkeerkans(boundingBox, ParkeerkansService.MONDAY, 10),
        this.wegdelenService.getWegdelen(boundingBox))
      .subscribe(this.showWegdelen.bind(this), this.showError);
  }

  private showWegdelen([parkeerkans, wegdelen]) {
    console.log('parkeerkans', parkeerkans);
    console.log('wegdelen', wegdelen);
    wegdelen.forEach((wegdeel) => {
      const wegdeelKans = parkeerkans[wegdeel.properties.id];
      wegdeel.bezetting = wegdeelKans ? wegdeelKans.bezetting : 0;
      this.highlightService.addMarker(this.leafletMap, wegdeel);
    });
  }

  private showError(error) {
    console.error(error);
  }
}
