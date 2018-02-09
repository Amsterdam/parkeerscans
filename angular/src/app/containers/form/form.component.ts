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
import { Store } from '@ngrx/store';
import { State as MapState } from '../../reducers/map';
import { SetSelectionAction } from '../../actions/map';
import { config } from './form.component.config';

@Component({
  selector: 'dp-form',
  changeDetection: ChangeDetectionStrategy.OnPush,
  templateUrl: './form.html',
  styleUrls: [
    './form.scss'
  ]
})
export class FormComponent implements OnInit {
  public selection: FormGroup;
  public days = config.days;
  public hours = config.hours;
  public value = null;
  public weekDay = 0;

  constructor(
    @Inject(FormBuilder)
    private fb: FormBuilder,
    private store: Store<MapState>) {}

  public ngOnInit() {
    this.weekDay = (new Date().getDay() + 6) % 7;
    this.selection = this.fb.group({
      day: [''],
      dayLte: [`${this.weekDay}`],
      dayGte: [`${this.weekDay}`],
      hour: [''],
      hour_gte: [''],
      hour_lte: [''],
      month: [''],
      month_gte: [''],
      month_lte: [''],
      year: ['']
    });
    this.selection.valueChanges.subscribe((value) => {
      this.value = value;
    });
  }

  public reset() {
    this.selection.reset({
      day: '',
      dayLte: `${this.weekDay}`,
      dayGte: `${this.weekDay}`,
      hour: '',
      hour_gte: '',
      hour_lte: '',
      month: '',
      month_gte: '',
      month_lte: '',
      year: ''
    });
    this.value = null;
  }

  public request() {
    this.store.dispatch(new SetSelectionAction(this.value));
  }
}
