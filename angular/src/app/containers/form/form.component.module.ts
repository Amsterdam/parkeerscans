import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule  } from '@angular/forms';
import { LeafletModule } from '../leaflet';

import { FormComponent } from './form.component';

@NgModule({
  imports: [
    FormsModule,
    ReactiveFormsModule,
    LeafletModule
  ],
  declarations: [
    FormComponent
  ],
  exports: [
    FormComponent
  ]
})
export class FormModule {}
