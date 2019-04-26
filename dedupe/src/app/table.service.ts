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
    return this.http.get<any>('http://18.208.127.146:4200/getcsv');
  }
  getQues(){
    return this.http.get<any>('http://18.208.127.146:4200/getquestions');
  }
  postMatchData(data){
    return this.http.post<any>('http://18.208.127.146:4200/getnewcsv',data);
  }
}

