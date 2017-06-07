import { Action } from '@ngrx/store';

export const SET_SELECTION = '[Map] Set selection';

/**
 * Every action is comprised of at least a type and an optional
 * payload. Expressing actions as classes enables powerful
 * type checking in reducer functions.
 *
 * See Discriminated Unions:
 * https://www.typescriptlang.org/docs/handbook/advanced-types.html#discriminated-unions
 */
export class SetSelectionAction implements Action {
  public readonly type = SET_SELECTION;

  constructor(public payload: {day: string, hour: string, year: string, month: string}) { }
}

/**
 * Export a type alias of all actions in this action group
 * so that reducers can easily compose action types
 */
export type Actions = SetSelectionAction;
