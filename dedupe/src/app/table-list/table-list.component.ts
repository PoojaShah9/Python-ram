import { Component, OnInit,ViewChild } from '@angular/core';
import {TableService} from "../table.service";
// import {NgxSpinnerService} from "ngx-spinner";
import {Ng4LoadingSpinnerService} from "ng4-loading-spinner";

@Component({
  selector: 'app-table-list',
  templateUrl: './table-list.component.html',
  styleUrls: ['./table-list.component.css']
})
export class TableListComponent implements OnInit {
  datas:any = [];
  constructor(public TableService:TableService,
              private spinner:Ng4LoadingSpinnerService) {
  }


  ngOnInit() {
    this.getdata();
  }
    getdata(){
      this.spinner.show();
    this.TableService.getAlldata().subscribe(data=>{
      let d = data.result;
      this.datas = d;
      console.log("hi");
      this.spinner.hide();
    },
      error1 => {
        console.log('error', error1);
      });
    }

}
