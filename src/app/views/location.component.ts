import {Component, OnInit} from '@angular/core';
import {FormControl} from '@angular/forms';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import { Router } from '@angular/router';
import { Globals } from '../globals';


@Component({
  selector: 'location',
  template: `



    <h4>Choose your supermarket</h4>

    <div class="search-bar-wrapper">
      <div class="icon location">
      </div>

      <mat-form-field class="search-bar">
        <mat-label>Location</mat-label>
        <input type="text" matInput [formControl]="barFormControl" [matAutocomplete]="auto">
        <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn">
          <mat-option *ngFor="let supermarket of filteredOptions | async" (click)="choose($event, supermarket)" [value]="supermarket">
            {{supermarket}}
          </mat-option>
        </mat-autocomplete>
      </mat-form-field>

    </div>

    <div class="btn bottom" (click)="route()">Continue</div>


  `,
  styles: [
    
    `

      :host {
        display:block;
        padding: 20px 0px;
      }
    
      .search-bar-wrapper {

        display:flex;

      }

      .search-bar {

        margin-left: 10px;
        width: 100%
      }
    
    
    `

  ]
})
export class LocationComponent {

  public barFormControl = new FormControl()
  public supermarket: string    
  public supermarkets: string[] = [ 
    "Rewe",
    // "Rewe Südstadt",
    // "Edeka",
    // "Kaufland",
    // "Alnatura"
  ]
  
  filteredOptions: Observable<string[]>;
  

  constructor(public router: Router) {

    this.supermarket = Globals.supermarket
  }


  ngOnInit() {
    this.filteredOptions = this.barFormControl.valueChanges
      .pipe(
        startWith(''),
        map(value => typeof value === 'string' ? value : value.name),
        map(name => this._filter(name))
      );
  }

  displayFn(supermarket: string): string {
    return supermarket ? supermarket : '';
  }

  private _filter(name: string): string[] {
    const filterValue = name.toLowerCase();

    return this.supermarkets.filter(option => option.toLowerCase().indexOf(filterValue) === 0);
  }
  public route(){

    if(Globals.supermarket)
      this.router.navigateByUrl('/list')
  } 

  

  choose(e?, supermarket?:string){

    Globals.supermarket = this.supermarket = supermarket
  } 
}
