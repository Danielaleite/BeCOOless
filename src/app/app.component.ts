import { Component, AfterViewInit } from '@angular/core';
import { Router } from '@angular/router';
import { Globals } from './globals';

@Component({
  selector: 'app-root',
  template: `
  
    
  <div id="outlet-wrapper">
    <router-outlet></router-outlet>
  </div>


  `,
  styleUrls: ['./app.component.css']
})
export class AppComponent implements AfterViewInit {

  constructor(public router: Router) {

  }

  ngAfterViewInit() {

  } 

}
