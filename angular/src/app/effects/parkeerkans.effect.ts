// import 'rxjs/add/operator/map';
// import 'rxjs/add/operator/catch';
// import 'rxjs/add/operator/startWith';
// import 'rxjs/add/operator/switchMap';
// import 'rxjs/add/operator/mergeMap';
// import 'rxjs/add/operator/toArray';
// import { Injectable } from '@angular/core';
// import { Action } from '@ngrx/store';
// import { Effect, Actions } from '@ngrx/effects';
// import { Database } from '@ngrx/db';
// import { Observable } from 'rxjs/Observable';
// import { defer } from 'rxjs/observable/defer';
// import { of } from 'rxjs/observable/of';
//
// import { ParkeerkansService } from '../../services/parkeerkans';
//
// @Injectable()
// export class SelectWegdeelEffects {
//
//   @Effect()
//   public load$: Observable<Action> = this.actions$
//     .ofType('SELECT_WEGDEEL')
//     .switchMap(() =>
//       ParkeerkansService
//         .getParkeerkans('4.884999621387469,52.37645412785948,' +
//           '4.887127107738007,52.377726757994324')
//         .subscribe((result) => {
//           return Observable.of({ type: 'SELECT_WEGDEEL_SUCCESS', payload: result });
//         })
//     );
//
//   constructor(private actions$: Actions, private parkeerkansService: ParkeerkansService) {}
// }
