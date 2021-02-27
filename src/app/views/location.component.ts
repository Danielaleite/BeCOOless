import {Component, OnInit} from '@angular/core';
import {FormControl} from '@angular/forms';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import { BuyingItem } from './buying-item';
import { Router } from '@angular/router';


@Component({
  selector: 'init',
  template: `


    <mat-form-field>
      <mat-label>Location</mat-label>
      <input type="text" matInput [formControl]="barFormControl" [matAutocomplete]="auto">
      <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn">
        <mat-option *ngFor="let item of filteredOptions | async" [value]="item">
          {{item.name}}
        </mat-option>
      </mat-autocomplete>
    </mat-form-field>

    <div>
      <button mat-raised-button color="primary" (click)="route()">Ready</button>
    </div>
  `,
})
export class LocationComponent {

  public barFormControl = new FormControl()
  public buyingList: BuyingItem[] = []
    
  public items: BuyingItem[] = [
    {
      name: 'A',
      category: 'AA',
      price: 10,
      co2: 5
    },
    {
      name: 'B',
      category: 'BB',
      price: 15,
      co2: 55
    },
  ]
  
  filteredOptions: Observable<BuyingItem[]>;
  

  constructor(public router: Router) {

  }


  ngOnInit() {
    this.filteredOptions = this.barFormControl.valueChanges
      .pipe(
        startWith(''),
        map(value => typeof value === 'string' ? value : value.name),
        map(name => name ? this._filter(name) : this.items.slice())
      );
  }

  displayFn(user: BuyingItem): string {
    return user && user.name ? user.name : '';
  }

  private _filter(name: string): BuyingItem[] {
    console.log(name)
    const filterValue = name.toLowerCase();

    return this.items.filter(option => option.name.toLowerCase().indexOf(filterValue) === 0);
  }
  public route(){

    this.router.navigateByUrl('/list')
  } 
}
