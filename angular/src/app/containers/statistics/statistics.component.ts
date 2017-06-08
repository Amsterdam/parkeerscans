import {
  ChangeDetectionStrategy,
  Component,
  Inject,
  OnInit
} from '@angular/core';
import {
  FormBuilder,
  FormGroup,
} from '@angular/forms';
import { Observable } from 'rxjs/Rx';
import { Store } from '@ngrx/store';

import { WegdelenService } from '../../services/wegdelen';
import { State as SelectedWegdeelState } from '../../reducers/selected-wegdeel.reducer';
import { SetSelectionAction } from '../../actions/map';
import { config } from './form.component.config';

@Component({
  selector: 'dp-statistics',
  templateUrl: './statistics.html',
  styleUrls: [
    './statistics.scss'
  ]
})
export class StatisticsComponent implements OnInit {
  public bezetting: any;
  public chartData: any[];
  private selectedWegdeel$: Observable<any>;

  constructor(
      private store: Store<SelectedWegdeelState>,
      private wegdelenService: WegdelenService) {
    this.selectedWegdeel$ = store.select('selectedWegdeel');
  }

  public ngOnInit() {
    this.selectedWegdeel$.subscribe((value) => {
      this.wegdelenService.getBezetting(value.id).subscribe((res) => {
        if (!res.wegdelen[res.selection.bgt_wegdeel]) {
          return;
        }
        const mappedMetingen = [];
        res.wegdelen[res.selection.bgt_wegdeel].cardinal_vakken_by_day
            .forEach((day) => {
          day[1].forEach((meting) => {
            if (!mappedMetingen.some((met) => met[0] === `${meting[0]}:00`)) {
              mappedMetingen.push([meting[0] + ':00', meting[1]]);
            }
          });
        });
        this.chartData = mappedMetingen.sort((a, b) => {
          if (parseInt(a[0].substr(0, 2), 10) < parseInt(b[0].substr(0, 2), 10)) {
            return -1;
          }
          if (parseInt(a[0].substr(0, 2), 10) > parseInt(b[0].substr(0, 2), 10)) {
            return 1;
          }
          // a must be equal to b
          return 0;
        });
      });
    });
  }
}
