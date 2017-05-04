import { DBSchema } from '@ngrx/db';

/**
 * ngrx/db uses a simple schema config object to initialize stores in IndexedDB.
 */
export const schema: DBSchema = {
  version: 1,
  name: 'datapunt_app',
  stores: {
    map: {
      autoIncrement: true,
      primaryKey: 'id'
    }
  }
};
