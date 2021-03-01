import { Component } from "@angular/core";
import { Router } from "@angular/router";
@Component({
  selector: "login",
  template: `
  
   
  <div id="login-wrapper">

    <div style="text-align:center;"><img style="height: 200px;" src="./assets/images/logo.svg" /></div>

    <div class="btn" (click)="route()">Login</div>
    <div class="btn" (click)="route()">Register</div>
    <div class="btn" (click)="route()">Guest</div>

  </div>



  `,
  styles: [
    `

    #login-wrapper {
        display:flex;
        align-items:center;
        flex-direction: column;
        text-align:center;
    }
    #login-wrapper img {

        height: 100px;
    }
    #login-wrapper .btn {

        margin-top: 20px;
    }

    `,
  ],
})
export class LoginComponent {

  constructor(public router: Router) {

  }

  
  public route(){

    this.router.navigateByUrl('/location')
  } 
}