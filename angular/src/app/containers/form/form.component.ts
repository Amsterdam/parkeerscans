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

  constructor(
    @Inject(FormBuilder)
    private fb: FormBuilder,
    private store: Store<MapState>) {}

  public ngOnInit() {
    this.selection = this.fb.group({
      day: ['Weekdag'],
      day_lte: ['Tot weekdag'],
      day_gte: ['Vanaf weekdag'],
      hour: ['Tijdvak'],
      month: ['Maand'],
      year: ['Vanaf jaar']
    });
    this.selection.valueChanges.subscribe((value) => {
      this.store.dispatch(new SetSelectionAction(value));
    });
  }

  public reset() {
    this.selection.reset({
      day: 'Weekdag',
      day_lte: 'Tot weekdag',
      day_gte: 'Vanaf weekdag',
      hour: 'Tijdvak',
      month: 'Maand',
      year: 'Vanaf jaar'
    });
  }
}
