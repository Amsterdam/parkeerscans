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
  private map$: Observable<any>;
  private selectedWegdeel$: Observable<any>;

  constructor(
      private store: Store<SelectedWegdeelState>,
      private wegdelenService: WegdelenService) {
    this.selectedWegdeel$ = store.select('selectedWegdeel');
    this.map$ = store.select('map');
  }

  public ngOnInit() {
    Observable.combineLatest(this.map$, this.selectedWegdeel$).subscribe((state) => {
      const [mapState, selectedWegdeelState] = state;

      console.log(mapState);

      this.wegdelenService.getBezetting(selectedWegdeelState.id, mapState.selection.day,
          mapState.selection.dayGte, mapState.selection.dayLte, mapState.selection.hour,
          mapState.selection.year, mapState.selection.month)
          .subscribe((res) => {
        if (!res.wegdelen[res.selection.bgt_wegdeel]) {
          return;
        }
        const metingen = res.wegdelen[res.selection.bgt_wegdeel].cardinal_vakken_by_day
            .map((meting) => meting[1])
            .reduce((a, b) => a.concat(b), [])
            .map((meting) => ({ uur: meting[0], bezetting: meting[1] }));

        this.chartData = ['08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
            '20', '21', '22', '23', '00', '01', '02', '03', '04']
            .map((xPoint) => {
          const xPointMetingen = metingen.filter((meting) => meting.uur === Number(xPoint));
          return [
            xPoint,
            xPointMetingen.reduce((prev, curr) => {
              return prev + curr.bezetting;
            }, 0) / xPointMetingen.length || 0,
            10
          ];
        });
      });
    });
  }
}
