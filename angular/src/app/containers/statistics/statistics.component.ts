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
  public view: string;
  private map$: Observable<any>;
  private selectedWegdeel$: Observable<any>;

  constructor(
      private store: Store<SelectedWegdeelState>,
      private wegdelenService: WegdelenService) {
    this.selectedWegdeel$ = store.select('selectedWegdeel');
    this.map$ = store.select('map');
    this.view = 'week';
  }

  public ngOnInit() {
    this.processStatistics();
  }

  public toggleView(view) {
    this.processStatistics();
    this.view = view;
  }

  private processStatistics() {
    Observable.combineLatest(this.map$, this.selectedWegdeel$).subscribe((state) => {
      const [mapState, selectedWegdeelState] = state;

      this.wegdelenService.getBezetting(selectedWegdeelState.id, mapState.selection.day,
          mapState.selection.dayGte, mapState.selection.dayLte, mapState.selection.hour,
          mapState.selection.year, mapState.selection.month)
          .subscribe((res) => {
        if (!res.wegdelen[res.selection.bgt_wegdeel]) {
          return;
        }

        if (this.view === 'week') {
          const dagenMap = {
            0: 'Ma',
            1: 'Di',
            2: 'Wo',
            3: 'Do',
            4: 'Vr',
            5: 'Za',
            6: 'Zo'
          };

          const metingen = res.wegdelen[res.selection.bgt_wegdeel].cardinal_vakken_by_day
              .map((meting) => meting[1].map((_meting) => {
                console.log(meting[0], new Date(meting[0]).getDay());
                _meting[0] = dagenMap[new Date(meting[0]).getDay()];
                console.log(_meting[0]);
                return _meting;
              }))
              .reduce((a, b) => a.concat(b), [])
              .map((meting) => ({ dag: meting[0], bezetting: meting[1] }));

          this.chartData = ['Ma', 'Di', 'Wo', 'Do', 'Vr', 'Za', 'Zo'].map((xPoint) => {
            const xPointMetingen = metingen.filter((meting) => meting.dag === xPoint);
            return [
              xPoint,
              xPointMetingen.reduce((prev, curr) => prev + curr.bezetting, 0) /
                  xPointMetingen.length || 0
            ];
          });
        } else if (this.view === 'day') {
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
        }
      });
    });
  }
}
