import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Parkeerkans } from '../models/parkeerkans';

@Injectable()
export class ParkeerkansService {
  public static const MONDAY = 'monday';
  public static const TUESDAY = 'tuesday';
  public static const WEDNESDAY = 'wednesday';
  public static const THURSDAY = 'thursday';
  public static const FRIDAY = 'friday';
  public static const SATURDAY = 'saturday';
  public static const SUNDAY = 'sunday';

  private API_ROOT = 'https://acc.api.data.amsterdam.nl/';
  private API_PATH = 'predictiveparking/metingen/aggregations/wegdelen/';

  constructor(private http: Http) {}

  public getParkeerkans(
      boundingBox: string,
      day: string,
      hour: number): Observable<Parkeerkans> {

    return this.http.get(`${this.API_ROOT}${this.API_PATH}?` +
        `bbox=${boundingBox}`)
      .map((res) => res.json() || {})
      .catch((error) => Observable.throw(error.toString()));
  }
}
