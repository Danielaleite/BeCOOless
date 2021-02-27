import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'init',
  template: `
  

    <div>
        <h1>Welcome</h1>
        <p>bla bla bla</p>
    </div>
    
    <div class="input-wrapper">
      <div class="input-label">Threshold</div>
      <mat-slider class="slider"
        thumbLabel
        step="1"
        min="1"
        max="100">
      </mat-slider>
    </div>
  
    <div>
      <button mat-raised-button color="primary" (click)="route()">Ready</button>
    </div>

  
  `,
  styles: [
    `
    
    `
  ] 
})
export class InitComponent {

  constructor(public router: Router){


  } 

  public route(){

    this.router.navigateByUrl('/location')
  } 
}
