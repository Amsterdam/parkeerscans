import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Parkeerkans } from '../../models/parkeerkans';

@Injectable()
export class ParkeerkansService {
  public static MONDAY = 'monday';
  public static TUESDAY = 'tuesday';
  public static WEDNESDAY = 'wednesday';
  public static THURSDAY = 'thursday';
  public static FRIDAY = 'friday';
  public static SATURDAY = 'saturday';
  public static SUNDAY = 'sunday';

  private API_ROOT = 'https://acc.api.data.amsterdam.nl/';
  private API_PATH = 'predictiveparking/metingen/aggregations/wegdelen/';

  constructor(private http: Http) {}

  // DIT IS GEEN PARKEERKANS. DIT IS BEZETTING!

  public getParkeerkans(
      boundingBox: string,
      day: string,
      daygte: string,
      daylte: string,
      hour: string,
      hourgte: string,
      hourlte: string,
      year: string,
      month: string,
      ): Observable<Parkeerkans> {

    const dayString = day ? `day=${day}&` : '';
    const daylteString = daylte ? `day_lte=${daylte}&` : '';
    const daygteString = daygte ? `day_gte=${daygte}&` : '';
    const hourString = hour ? `hour=${hour}&` : '';
    const hourgteString = hourgte ? `hour_gte=${hourgte}&` : '';
    const hourlteString = hourlte ? `hour_lte=${hourlte}&` : '';
    const dategte = year ? `date_gte=${year}&` : '';
    const monthString = month ? `month=${month}&` : '';

    return this.http.get(`${this.API_ROOT}${this.API_PATH}?` +
        dayString +
        daylteString +
        daygteString +
        hourString +
        hourgteString +
        hourlteString +
        dategte +
        monthString +
        `bbox=${boundingBox}`)
      .map((res) => res.json() || {})
      .catch((error) => Observable.throw(error.toString()));
  }
}
