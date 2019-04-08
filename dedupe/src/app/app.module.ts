import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { TableListComponent } from './table-list/table-list.component';
import {HttpClientModule} from "@angular/common/http";
import { QuesComponent } from './ques/ques.component';
import {DataTablesModule} from "angular-datatables";

@NgModule({
  declarations: [
    AppComponent,
    TableListComponent,
    QuesComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    DataTablesModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
