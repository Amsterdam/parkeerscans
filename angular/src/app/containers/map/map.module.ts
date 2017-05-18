import { NgModule } from '@angular/core';
import { LeafletModule } from '../leaflet';

import { MapComponent } from './map.component';

@NgModule({
  imports: [
    LeafletModule
  ],
  declarations: [
    MapComponent
  ],
  exports: [
    MapComponent
  ]
})
export class MapModule {}
