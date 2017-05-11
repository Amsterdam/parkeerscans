import 'rxjs/add/operator/catch';
import 'rxjs/add/operator/map';
import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import { Observable } from 'rxjs/Observable';
import { Parkeerkans } from '../models/parkeerkans';

@Injectable()
export class ParkeervakService {
  private API_ROOT = 'https://acc.api.data.amsterdam.nl/';
  private API_PATH = 'predictiveparking/vakken/';

  constructor(private http: Http) {}

  public getParkeerkans(id: string): Observable<Parkeervak> {

    return this.http.get(`${this.API_ROOT}${this.API_PATH}${id}`)
      .map((res) => res.json() || {})
      .catch((error) => Observable.throw(error.toString()));
  }
}
