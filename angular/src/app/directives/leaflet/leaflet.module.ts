import { NgModule } from '@angular/core';
import { MapCrsModule } from '../../services/map-crs';
import { ParkeerkansModule } from '../../services/parkeerkans';
import { WegdelenModule } from '../../services/wegdelen';
import { ParkeervakkenModule } from '../../services/parkeervakken';

import { LeafletDirective } from './leaflet.directive';

@NgModule({
  imports: [
    MapCrsModule,
    ParkeerkansModule,
    WegdelenModule,
    ParkeervakkenModule
  ],
  declarations: [
    LeafletDirective
  ],
  exports: [
    LeafletDirective
  ]
})
export class LeafletModule {}
