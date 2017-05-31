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
import * as reducers from '../../reducers';
import { SetSelectionAction } from '../../actions/map';

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

  constructor(
    @Inject(FormBuilder)
    private fb: FormBuilder,
    private store: Store<reducers.State>) {}

  public ngOnInit() {
    this.selection = this.fb.group({
      day: [''],
      hour: ['']
    });
    this.selection.valueChanges.forEach((value) => {
      this.store.dispatch(new SetSelectionAction(value));
    });
  }
}
