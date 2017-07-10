import { Action } from '@ngrx/store';

import { Parkeervak } from '../models/parkeervak';

export const initialState: Parkeervak[] = [];

export const PARKEERVAKKEN_LOAD_FAILURE = 'PARKEERVAKKEN_LOAD_FAILURE';
export const PARKEERVAKKEN_LOAD_REQUEST = 'PARKEERVAKKEN_LOAD_REQUEST';
export const PARKEERVAKKEN_LOAD_SUCCES = 'PARKEERVAKKEN_LOAD_SUCCES';

export function parkeervakkenReducer(
    state: Parkeervak[] = initialState,
    action: Action): Parkeervak[] {
  switch (action.type) {
    case PARKEERVAKKEN_LOAD_REQUEST:
    case PARKEERVAKKEN_LOAD_FAILURE:
      return [...state];

    case PARKEERVAKKEN_LOAD_SUCCES:
      return [...action.payload];

    default:
      return state;
  }
}
