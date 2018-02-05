import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Wegdeel } from '../../models/wegdeel';

@Injectable()
export class WegdelenService {
  private API_ROOT = 'https://acc.map.data.amsterdam.nl/';
  private API_PATH = 'maps/predictiveparking';

  constructor(private http: Http) {}

  public getBezetting(
      wegdeelId: string,
      day: string,
      dayGte: string,
      dayLte: string,
      hour: string,
      year: string,
      month: string
  ): any {

    return this.http.get('https://acc.api.data.amsterdam.nl/predictiveparking' +
        '/metingen/aggregations/wegdelen/' +
        `?bgt_wegdeel=${wegdeelId}` +
        (day ? `&day=${day}` : '') +
        (dayGte ? `&day_gte=${dayGte}` : '&day_gte=0') +
        (dayLte ? `&day_lte=${dayLte}` : '&day_lte=6') +
        (hour ? `&hour=${hour}` : '&hour_gte=0&hour_lte=23') +
        (year ? `&year_gte=${year}` : '&year_gte=2017') +
        (month ? `&month=${month}` : '') +
        '&explain=true')
      .map((res) => res.json())
      .catch((error) => Observable.throw(error.toString()));
  }

  public getWegdelen(boundingBox: string): Observable<Wegdeel[]> {
    return this.http.get(`${this.API_ROOT}${this.API_PATH}?` +
        'REQUEST=Getfeature&' +
        'VERSION=1.1.0&' +
        'SERVICE=wfs&' +
        'TYPENAME=wegdelen&' +
        'srsName=EPSG:4326&' +
        'count=1500&' +
        'startindex=0&' +
        'outputformat=geojson&' +
        `bbox=${boundingBox}`)
      .map(this.parseResponse)
      .catch((error) => Observable.throw(error.toString()));
  }

  private parseResponse(response) {
    const json = response.json();
    return json ? json.features : [];
  }
}
