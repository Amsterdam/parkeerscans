import { Geometry } from './geometry';

export interface Wegdeel {
  type: any;
  properties: WegdeelProperties;
  geometry: Geometry;
}

interface WegdeelProperties {
  id: string;
  bezetting: string | number;
}
