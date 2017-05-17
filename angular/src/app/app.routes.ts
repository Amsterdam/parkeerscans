import { Routes } from '@angular/router';
import { MapComponent } from './containers/map.component';

import { DataResolver } from './app.resolver';

export const ROUTES: Routes = [
  { path: '',      component: MapComponent },
  { path: 'home',  component: MapComponent }
];
