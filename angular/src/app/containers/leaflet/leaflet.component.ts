import {
  AfterViewInit,
  Component,
  ElementRef,
  NgZone
} from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs/Rx';
import 'rxjs/add/operator/map';
import L from 'leaflet';
import 'leaflet-choropleth';
import { config } from './leaflet.component.config';
import { Parkeerkans } from '../../models/parkeerkans';
import { State as MapState } from '../../reducers/map';
import { MapCrs } from '../../services/map-crs';
import { ParkeerkansService } from '../../services/parkeerkans';
import { WegdelenService } from '../../services/wegdelen';
import { ParkeervakkenService } from '../../services/parkeervakken';

@Component({
  selector: 'dp-leaflet',
  template: '',
  styleUrls: [
    './leaflet.scss'
  ]
})
export class LeafletComponent implements AfterViewInit {
  private leafletMap: L.Map;
  private selection$: Observable<any>;
  private occupancy: {[wegdeelId: string]: number};
  private parkeervakkenLayer: any;
  private wegdelenLayer: any;
  private day;
  private dayGte;
  private dayLte;
  private hour;
  private year;
  private month;
  private mapSelection: any = {};
  private debounceHandler;
  private tooltip;

  constructor(
    private crs: MapCrs,
    private host: ElementRef,
    private parkeerkansService: ParkeerkansService,
    private parkeervakkenService: ParkeervakkenService,
    private store: Store<MapState>,
    private wegdelenService: WegdelenService,
    private zone: NgZone) {

    this.selection$ = store.select('map');
  }

  public ngAfterViewInit() {
    this.initLeaflet();
    this.updateBoundingBox();
    this.selection$.forEach((payload) => {
      if (payload) {
        this.day = payload.day;
        this.dayGte = payload.dayGte;
        this.dayLte = payload.dayLte;
        this.hour = payload.hour;
        this.year = payload.year;
        this.month = payload.month;
        this.updateBoundingBox();
      }
    });
  }

  private initLeaflet() {
    this.zone.run(() => {
      const options = Object.assign({}, config.map, {
        crs: this.crs.getRd()
      });
      this.leafletMap = L.map(this.host.nativeElement, options)
        .setView([52.3731081, 4.8932945], 11);
      const baseLayer = L.tileLayer('https://{s}.data.amsterdam.nl/topo_rd_zw/{z}/{x}/{y}.png', {
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

      this.leafletMap.on('moveend zoomend', this.updateBoundingBox.bind(this));
    });
  }

  private updateBoundingBox() {
    window.clearTimeout(this.debounceHandler);
    this.debounceHandler = window.setTimeout(function() {
      const boundingBox = this.leafletMap.getBounds();
      Observable
        .zip(
        this.parkeerkansService.getParkeerkans(
            boundingBox.toBBoxString(),
            this.day,
            this.dayGte,
            this.dayLte,
            this.hour, this.year, this.month),
          this.wegdelenService.getWegdelen(boundingBox.toBBoxString()))
        .subscribe(this.showWegdelen.bind(this), this.showError);
    }.bind(this), 500);
  }

  private showWegdelen([parkeerkans, wegdelen]: [Parkeerkans, any]) {
    this.occupancy = {};
    const data = wegdelen.map((wegdeel) => {
      const wegdeelKans = parkeerkans.wegdelen[wegdeel.properties.bgt_id];
      wegdeel.properties.bezetting = wegdeelKans ? wegdeelKans.avg_occupancy : undefined;
      this.occupancy[wegdeel.properties.bgt_id] = wegdeel.properties.bezetting;
      return wegdeel;
    }).filter((wegdeel) => {
      return wegdeel.properties.bezetting === 'fout' ? false
        : wegdeel.properties.bezetting !== undefined;
    });

    // Add entries with a bezetting of 0 and 100 to make sure choropleth takes the full percentage
    // range as the range for it's colors.
    data.push({ properties: { bezetting: 0 } });
    data.push({ properties: { bezetting: 100 } });

    if (this.wegdelenLayer !== undefined) {
      this.leafletMap.removeLayer(this.wegdelenLayer);
    }

    const extendedConfig = Object.assign({}, config.choropleth.wegdelen, {
      onEachFeature: (feature, layer) => {
        layer.on({
          mouseover: (e) => {
            this.tooltip = L.popup()
                .setLatLng(e.latlng)
                .setContent(feature.properties.bezetting.toFixed(2) +
                        `% van ${feature.properties.vakken} vakken`)
                .openOn(this.leafletMap);
          },
          mouseout: () => {
            this.leafletMap.closePopup(this.tooltip);
          }
        });
      }
    });

    this.wegdelenLayer = L.choropleth({
      type: 'FeatureCollection',
      features: data
    }, extendedConfig).addTo(this.leafletMap);

    const boundingBox = this.leafletMap.getBounds().toBBoxString();
    this.parkeervakkenService.getVakken(boundingBox)
      .subscribe(this.showParkeervakken.bind(this), this.showError);
  }

  private showParkeervakken(parkeervakken) {
    parkeervakken = parkeervakken
        .map((parkeervak) => {
          parkeervak.properties.bezetting = this.occupancy[parkeervak.properties.bgt_wegdeel];
          return parkeervak;
        }, this)
        .filter((parkeervak) => {
          return parkeervak.properties.bezetting !== undefined;
        });

    parkeervakken.push({ properties: { bezetting: 0 } });
    parkeervakken.push({ properties: { bezetting: 100 } });

    const extendedConfig = Object.assign({}, config.choropleth.parkeervakken, {
      onEachFeature: (feature, layer) => {
        layer.on({
          click: () => this.showStatistics(feature)
        });
      }
    });

    if (this.parkeervakkenLayer !== undefined) {
      this.leafletMap.removeLayer(this.parkeervakkenLayer);
    }

    this.parkeervakkenLayer = L.choropleth({
      type: 'FeatureCollection',
      features: parkeervakken
    }, extendedConfig).addTo(this.leafletMap);
  }

  private showStatistics(feature) {
    this.store.dispatch({
      type: 'SELECT_WEGDEEL',
      payload: {
        id: feature.properties.bgt_wegdeel
      }
    });
  }

  private showError(error) {
    console.error(error);
  }
}
