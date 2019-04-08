import { Component, OnInit,ViewChild } from '@angular/core';
import {TableService} from "../table.service";

@Component({
  selector: 'app-table-list',
  templateUrl: './table-list.component.html',
  styleUrls: ['./table-list.component.css']
})
export class TableListComponent implements OnInit {
  datas:any = [];
  constructor(public TableService:TableService) {
  }


  ngOnInit() {
    this.getdata();
  }
    getdata(){
    this.TableService.getAlldata().subscribe(data=>{
      console.log(data,'data');
      this.datas = data.result;
    },
      error1 => {
        console.log('error', error1);
      });
    }

}
