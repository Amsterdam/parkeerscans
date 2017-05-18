import { NgModule } from '@angular/core';
import { MapCrsModule } from 'app/services/map-crs';

import { LeafletComponent } from './leaflet.component';

@NgModule({
  imports: [
    MapCrsModule
  ],
  declarations: [
    LeafletComponent
  ],
  exports: [
    LeafletComponent
  ]
})
export class LeafletModule {}
