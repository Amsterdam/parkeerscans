import L from 'leaflet';
import 'leaflet-choropleth';
import 'rxjs/add/operator/map';
import { Directive, OnInit, ElementRef, Input, NgZone } from '@angular/core';
import { Observable } from 'rxjs/Rx';
import { MapCrs } from './map-crs.service';
import { ParkeerkansService } from '../services/parkeerkans.service';
import { WegdelenService } from '../services/wegdelen.service';
import { ParkeervakkenService } from '../services/parkeervakken.service';
import { HighlightService } from '../services/highlight.service';

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
    private parkeervakkenService: ParkeervakkenService,
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
      .setView([52.3626088, 4.9081912], 13);
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
    const data = wegdelen.map((wegdeel) => {
      const wegdeelKans = parkeerkans[wegdeel.properties.id];
      wegdeel.properties.bezetting = wegdeelKans ? wegdeelKans.bezetting : 0;
      return wegdeel;
    }).filter((wegdeel) =>
      wegdeel.properties.bezetting === 'fout' ? false : wegdeel.properties.bezetting
    );
    console.log('data', data);
    L.choropleth({
      type: 'FeatureCollection',
      features: data
    }, {
      valueProperty: 'bezetting',
      scale: ['white', 'red'],
      steps: 10,
      mode: 'q',
      style: {
        color: '#fff',
        weight: 2,
        fillOpacity: 0.8
      }
    }).addTo(this.leafletMap);

    const boundingBox = this.leafletMap.getBounds().toBBoxString();
    this.parkeervakkenService.getVakken(boundingBox)
      .subscribe(this.showParkeervakken.bind(this), this.showError);
  }

  private showParkeervakken(parkeervakken) {
    L.choropleth({
      type: 'FeatureCollection',
      features: parkeervakken
    }, {
      valueProperty: 'scan_count',
      scale: ['white', 'green'],
      steps: 10,
      mode: 'q',
      style: {
        color: '#fff',
        weight: 2,
        fillOpacity: 0.8
      }
    }).addTo(this.leafletMap);
  }

  private showError(error) {
    console.error(error);
  }
}
