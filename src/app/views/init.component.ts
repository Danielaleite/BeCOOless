import { Component } from "@angular/core";
import { Router } from "@angular/router";
@Component({
  selector: "init",
  template: `
  
   
  <div>

    <div class="logo-wrapper">

      <img src="./assets/images/logo.png"/>
      
    </div>

    <div style="margin-bottom: 10%;">

      <h4>Be COOL</h4> 
      
    </div>
    
    <div>

      <span>Go green. Be COO-Less</span> 
      
    </div>
    
      <div class="btn bottom" (click)="route()">Get started</div>

  </div>



  `,
  styles: [
    `
    :host {
      text-align:center;
    }

    .logo-wrapper {
      display: flex;
      justify-content:center;
      align-items:center;
      width: 100%;
      max-width: 500px;
      margin-top: 20%;
      margin-bottom: 20%;
    }

    .logo-wrapper img {
      width:70%;
    }



    `,
  ],
})
export class InitComponent {

  constructor(public router: Router) {

  }

  
  public route(){

    this.router.navigateByUrl('/login')
  } 
}