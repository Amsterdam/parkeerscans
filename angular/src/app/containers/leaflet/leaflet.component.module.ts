import { NgModule } from '@angular/core';
import { MapCrsModule } from '../../services/map-crs';
import { ParkeerkansModule } from '../../services/parkeerkans';
import { WegdelenModule } from '../../services/wegdelen';
import { ParkeervakkenModule } from '../../services/parkeervakken';

import { LeafletComponent } from './leaflet.component';

@NgModule({
  imports: [
    MapCrsModule,
    ParkeerkansModule,
    WegdelenModule,
    ParkeervakkenModule
  ],
  declarations: [
    LeafletComponent
  ],
  exports: [
    LeafletComponent
  ]
})
export class LeafletModule {}
