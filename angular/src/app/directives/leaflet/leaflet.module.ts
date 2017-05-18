import { NgModule } from '@angular/core';
import { MapCrsModule } from 'app/services/map-crs';

import { LeafletDirective } from './leaflet.directive';

@NgModule({
  imports: [
    MapCrsModule
  ],
  declarations: [
    LeafletDirective
  ],
  exports: [
    LeafletDirective
  ]
})
export class LeafletModule {}
