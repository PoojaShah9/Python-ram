import { Component, OnInit,ViewChild } from '@angular/core';
import {TableService} from "../table.service";
import {NgxSpinnerService} from "ngx-spinner";
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
    this.spinner.show();

    setTimeout(() => {
      /** spinner ends after 5 seconds */
      this.spinner.hide();
    }, 5000);

    this.getdata();
  }
    getdata(){
    this.spinner.show();
    this.TableService.getAlldata().subscribe(data=>{
      console.log(data,'data');
      let d = data.result;
      this.spinner.hide();
    //  d= d.replace('\\','');
      console.log("fgfdg", d);
      this.datas = d;
    },
      error1 => {
        console.log('error', error1);
      });
    }

}
