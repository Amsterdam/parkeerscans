import { Component, ChangeDetectionStrategy } from '@angular/core';
import { Store } from '@ngrx/store';
import { Observable } from 'rxjs/Observable';

import * as fromRoot from '../reducers';
import * as mapActions from '../actions/map';

@Component({
  selector: 'dp-map',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `<div dp-leaflet class="c-map"></div>`
})
export class MapComponent {
}
