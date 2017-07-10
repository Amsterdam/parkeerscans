import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LeafletModule } from '../leaflet';
import { FormModule } from '../form';
import { StatisticsModule } from '../statistics';

import { MapComponent } from './map.component';

@NgModule({
  imports: [
    CommonModule,
    LeafletModule,
    FormModule,
    StatisticsModule
  ],
  declarations: [
    MapComponent
  ],
  exports: [
    MapComponent
  ]
})
export class MapModule {}
