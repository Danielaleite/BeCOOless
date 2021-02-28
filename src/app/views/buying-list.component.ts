import {AfterViewInit, Component, OnInit} from '@angular/core';
import {FormControl} from '@angular/forms';
import {Observable} from 'rxjs';
import {map, startWith} from 'rxjs/operators';
import { BuyingItem } from './buying-item';
import { Router } from '@angular/router';
import { Globals } from '../globals';
import { ItemService } from '../provider/item.service';


@Component({
  selector: 'init',
  template: `


    <mat-form-field class="search-bar">
      <mat-label>Search {{ supermarket }}</mat-label>
      <input type="text" id="item-input" matInput [formControl]="barFormControl" [matAutocomplete]="auto" >
      <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn">
        <mat-option *ngFor="let item of filteredOptions | async" (click)="add($event, item)" [value]="item">
          {{item.name}}
        </mat-option>
      </mat-autocomplete>
    </mat-form-field>




    <div id="buying-list-wrapper">

      <ul>
        <li *ngFor="let item of items">
            
          <div>{{ item.name }}</div>
          <div><img src="./assets/images/empty-image.jpg" /></div>

          <div class="item-bar">
            <div class="icon plus" (click)="add($event, item)"><div>+</div></div>
            <div class="item-amount">{{item.amount}}</div>
            <div class="icon minus" (click)="remove($event, item)"><div>-</div></div>
          </div>

        </li>
      </ul>

    </div>

  
    <div class="btn bottom-side" (click)="route()">Reduce CO2</div>

  `,
  styles: [
    `
    
      .search-bar {
        width: 100%;
      }


      #buying-list-wrapper {

      }
      
      #buying-list-wrapper ul {
      }
    
      #buying-list-wrapper ul li {
        position: relative;
        display: inline-block;
        width: 50%;
        height: 200px;
        box-sizing:border-box;
        padding: 2.5%;
        text-align:center;
        cursor:pointer;
      }
      #buying-list-wrapper ul li img {
        width: 100%;
      }

      #buying-list-wrapper ul li .item-bar {
    
        position:absolute;
        bottom: 0px;
        display: flex;
        justify-content:center;
        width: 90%;
      }

      #buying-list-wrapper ul li .item-bar div {
        width: 33%;
        cursor:pointer;
        display:flex;
        justify-content: center;
        align-items: center;
        box-sizing:border-box;
      }

      #buying-list-wrapper ul li .item-bar div div {
        box-sizing:border-box;
        width: 30px;
        height: 30px;
        background-color: #1FCC79;
        color: #fff;
        border-radius: 100%;

        user-select: none;
        -moz-user-select: none;
        -khtml-user-select: none;
        -webkit-user-select: none;
        -o-user-select: none;
      }

    `
  ]
})
export class BuyingListComponent implements AfterViewInit {

  public barFormControl = new FormControl()
  public buyingList: BuyingItem[] = []
    
  public items: BuyingItem[] = [
    {
      name: 'A',
      amount: 0,
      category: 'AA',
      price: 10,
      co2: 5
    },
    {
      name: 'B',
      amount: 0,
      category: 'BB',
      price: 15,
      co2: 55
    },
    {
      name: 'C',
      amount: 0,
      category: 'BB',
      price: 15,
      co2: 55
    },
  ]
  
  filteredOptions: Observable<BuyingItem[]>;
  

  constructor(public router: Router, public itemService: ItemService) {

    itemService.query('BLUB')
  }

  get supermarket() {

    return Globals.supermarket
  }


  ngOnInit() {
    this.filteredOptions = this.barFormControl.valueChanges
      .pipe(
        startWith(''),
        map(value => typeof value === 'string' ? value : value.name),
        map(name => name ? this._filter(name) : this.items.slice())
      );
  }

  ngAfterViewInit() {


  }

  displayFn(user: BuyingItem): string {
    return user && user.name ? user.name : '';
  }

  private _filter(name: string): BuyingItem[] {
    const filterValue = name.toLowerCase();

    return this.items.filter(option => option.name.toLowerCase().indexOf(filterValue) === 0);
  }
  public route(){

    if(this.buyingList.length > 0)
      this.router.navigateByUrl('/compare')
  } 



  add(e?, addItem?:BuyingItem) {

    for(let item of this.buyingList) {

      if(item == addItem) {

        item.amount += 1
        return true
      }
    }

    for(let item of this.items) {

      if(item.name == addItem.name) {

        addItem.amount +=1
        this.buyingList.push(addItem)
        return true
      } 
    } 
    return false
  } 

  remove(e?, item?:BuyingItem) {

    if(item && item.amount > 0) item.amount -= 1
  } 

}
