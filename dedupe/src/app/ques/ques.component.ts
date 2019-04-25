import { Component, OnInit } from '@angular/core';
import {TableService} from "../table.service";
import {Ng4LoadingSpinnerService} from "ng4-loading-spinner";

@Component({
  selector: 'app-ques',
  templateUrl: './ques.component.html',
  styleUrls: ['./ques.component.css']
})
export class QuesComponent implements OnInit {
  value:any = [];
  matchData:any ={};
  index = 1;
  showQuestions = true;
  finaldata:any = [];
  constructor(public TableService:TableService,
              private spinner:Ng4LoadingSpinnerService) {}


  ngOnInit() {
    this.getAllQues();
    this.matchData.match = [];
    this.matchData.distinct = [];
  }

  getAllQues(){
    this.spinner.show();
    this.TableService.getQues().subscribe(data=>{
        console.log(data,'data');
        this.value = data.result;
        this.spinner.hide();
      },
      error1 => {
        console.log('error', error1);
      });
  }

  setAnswer(value, data){
    this.index += 1
    if(value === 'y'){
      //this.matchData.match.push(Object.assign({}, data));
      this.matchData.match.push(data);
    }else if(value === 'n'){
      this.matchData.distinct.push(data);
    }
    this.getAllQues()
  }

  terminateData(){
    let final = {'final' : this.matchData}
    //console.log('final Records' , JSON.stringify(this.matchData));
    this.showQuestions = false;
    this.spinner.show();
    this.TableService.postMatchData(final).subscribe(final=>{
      this.finaldata = final.result;
      this.spinner.hide();
    })

  }


}
