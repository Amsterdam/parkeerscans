import * as mapActions from '../actions/map';

export interface State {
  selection: {
    day: string;
    dayLte: string;
    dayGte: string;
    hour: string;
    month: string;
    year: string;
  };
}

export const initialState: State = {
  selection: {
    day: '',
    dayLte: '',
    dayGte: '',
    hour: '',
    month: '',
    year: ''
  }
};

export function mapReducer(state = initialState, action: mapActions.Actions): State {
  switch (action.type) {
    case mapActions.SET_SELECTION: {
      return {
        selection: action.payload
      };
    }

    default: {
      return state;
    }
  }
}

export const getSelection = (state: State) => state.selection;
