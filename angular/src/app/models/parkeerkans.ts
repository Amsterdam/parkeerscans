export interface Parkeerkans {
  [key: string]: WegdeelInfo;
}

interface WegdeelInfo {
  scans: number;
}
