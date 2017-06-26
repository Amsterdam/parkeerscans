import { Action } from '@ngrx/store';

import { Wegdeel } from '../models/wegdeel';

export const initialState: Wegdeel[] = [];

export const WEGDELEN_LOAD_FAILURE = 'WEGDELEN_LOAD_FAILURE';
export const WEGDELEN_LOAD_REQUEST = 'WEGDELEN_LOAD_REQUEST';
export const WEGDELEN_LOAD_SUCCES = 'WEGDELEN_LOAD_SUCCES';

export function wegdelenReducer(state: Wegdeel[] = initialState, action: Action): Wegdeel[] {
  switch (action.type) {
    case WEGDELEN_LOAD_REQUEST:
    case WEGDELEN_LOAD_FAILURE:
      return [...state];

    case WEGDELEN_LOAD_SUCCES:
      return [...action.payload];

    default:
      return state;
  }
}
