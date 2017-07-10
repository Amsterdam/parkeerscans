import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';

import { BarChartComponentModule } from '../../components/bar-chart';
import { StatisticsComponent } from './statistics.component';

@NgModule({
  imports: [
    CommonModule,
    BarChartComponentModule
  ],
  declarations: [
    StatisticsComponent
  ],
  exports: [
    StatisticsComponent
  ]
})
export class StatisticsModule {}
