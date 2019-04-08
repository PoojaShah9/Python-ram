import { Injectable } from '@angular/core';
import { HttpClient} from '@angular/common/http';
// var data = require('src/app/data.json');

@Injectable({
  providedIn: 'root'
})
export class TableService {
  constructor(private http: HttpClient) {
  }
  getAlldata(){
    // return data;
    return this.http.get<any>('assets/json/data.json');
  }
  getQues(){
    return this.http.get<any>('assets/json/ques.json');
  }
}
