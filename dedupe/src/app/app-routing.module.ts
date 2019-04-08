import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {QuesComponent} from "./ques/ques.component";
import {TableListComponent} from "./table-list/table-list.component";

const routes: Routes = [
  {path: '', component: TableListComponent},
  {path: 'ques',component: QuesComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
