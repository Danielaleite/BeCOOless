import { Component } from "@angular/core";
import { Router } from "@angular/router";
@Component({
  selector: "init",
  template: `
  
   
  <div id="login-wrapper">

    <div><img src="./assets/images/login.png" /></div>

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
    }
    #login-wrapper img {

        width: 100%;
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