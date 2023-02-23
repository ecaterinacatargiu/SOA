import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from 'src/environments/environments';
import { TwitterData } from '../model/TwitterData.model';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class TwitterDataService {

  constructor(private httpClient: HttpClient) { }


  getAll(): Observable<TwitterData[]>
  {
    return this.httpClient.get<Array<TwitterData>>(`${environment.serverURL}/all`)
  }

  getLast_Hour()
  {
    return this.httpClient.get<Array<TwitterData>>(`${environment.serverURL}/last_hour`)
  }

  getLast_Day()
  {
    return this.httpClient.get<Array<TwitterData>>(`${environment.serverURL}/last_day`)
  }
}
