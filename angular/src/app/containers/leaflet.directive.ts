import { Directive, ElementRef, Input } from '@angular/core';
import L from 'leaflet';

@Directive({ selector: '[dp-leaflet]' })
export class LeafletDirective {
  constructor(el: ElementRef) {
    const leafletMap: L.Map = L.map(el.nativeElement, {
      center: [52.3731081, 4.8932945],
      zoom: 11,
    });
  }
}
