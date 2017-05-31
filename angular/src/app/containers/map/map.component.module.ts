import { NgModule } from '@angular/core';
import { LeafletModule } from '../leaflet';
import { FormModule } from '../form';

import { MapComponent } from './map.component';

@NgModule({
  imports: [
    LeafletModule,
    FormModule
  ],
  declarations: [
    MapComponent
  ],
  exports: [
    MapComponent
  ]
})
export class MapModule {}
