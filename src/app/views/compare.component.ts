import { Component } from "@angular/core";
import { Router } from "@angular/router";
@Component({
  selector: "init",
  template: `
  
   

  `,
  styles: [
    `

    `,
  ],
})
export class CompareComponent {

  constructor(public router: Router) {

  }

  
  public route(){

    this.router.navigateByUrl('/location')
  } 
}