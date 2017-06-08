import { Action } from '@ngrx/store';

export interface State {
  fetching?: boolean;
  id: number;
}

export const initialState: State = {
  id: null
};

export const SELECT_WEGDEEL = 'SELECT_WEGDEEL';
export const SELECT_WEGDEEL_SUCCESS = 'SELECT_WEGDEEL_SUCCESS';

export function selectedWegdeelReducer(state: State = initialState, action: Action): State {
  switch (action.type) {
    case SELECT_WEGDEEL:
      return Object.assign({}, action.payload, { fetching: true });

    case SELECT_WEGDEEL_SUCCESS:
      return Object.assign({}, action.payload, { fetching: false });

    default:
      return state;
  }
}
