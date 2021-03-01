import {AfterViewInit, Component, OnInit} from '@angular/core';
import {FormControl} from '@angular/forms';
import {Observable} from 'rxjs';
import {filter, map, startWith} from 'rxjs/operators';
import { Router } from '@angular/router';
import { Globals } from '../globals';
import { ItemService } from '../provider/item.service';
import { ShoppingItem } from './shopping-item';
import { DB } from '../data';


@Component({
  selector: 'buying-list',
  template: `


  <div class="search-bar-wrapper">
    
    <mat-form-field class="search-bar">
      <mat-label>Search in {{ supermarket }}</mat-label>
      <input type="text" id="item-input" matInput [formControl]="barFormControl" [matAutocomplete]="auto" >
      <mat-autocomplete #auto="matAutocomplete" [displayWith]="displayFn">
        
      </mat-autocomplete>
    </mat-form-field>

    <div class="icon basket">
      <div *ngIf="basketAmount > 0" class="basket-notification">{{ basketAmount }}</div>
    </div>
  </div>



    <div id="buying-list-wrapper">

      <ul>
        <li *ngFor="let item of filteredOptions | async">
            
          <div>{{ item.name }}</div>
          <div><img [src]="item.img" /></div>

          <div class="item-bar">
            <div class="icon plus" (click)="add($event, item)"><div>+</div></div>
            <div class="item-amount">{{item.amount}}</div>
            <div class="icon minus" (click)="remove($event, item)"><div>-</div></div>
          </div>

        </li>
      </ul>

    </div>

  
    <div class="btn bottom-fixed" (click)="route()">Reduce CO2</div>

  `,
  styles: [
    `
    
    .search-bar-wrapper {

      display:flex;

    }
    .search-bar {
      width: 100%;
    }
    .search-bar-wrapper .icon.basket { 

      position:relative;
    }

    .basket-notification {

      position:absolute;
      right: 0px;
      top: 0px;

      width: 20px;
      height: 20px;
      line-height: 20px;
      text-align:center;
      font-size: .7rem;

      background-color: #1FCC79;
      border-radius: 100%;
    }


      #buying-list-wrapper {
        margin-bottom: 100px;
      }
      
      #buying-list-wrapper ul {
      }
    
      #buying-list-wrapper ul li {
        position: relative;
        display: inline-block;
        width: 50%;
        box-sizing:border-box;
        padding: 2.5%;
        text-align:center;
        cursor:pointer;
        margin-bottom: 20px;
      }
      #buying-list-wrapper ul li img {
        width: 100%;
      }

      #buying-list-wrapper ul li .item-bar {
    
        position:absolute;
        bottom: -30px;
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



      .btn.bottom-fixed {

        position: fixed;

        bottom: 20px;
        left: 10%
      }
    `
  ]
})
export class BuyingListComponent implements AfterViewInit {

  public barFormControl = new FormControl()
  public get buyingList() {

    return Globals.shoppingList
  }

  public get basketAmount() :number {
    return this.buyingList.length
  }

  public items: ShoppingItem[] = []
  
  filteredOptions: Observable<ShoppingItem[]>;
  

  constructor(public router: Router, public itemService: ItemService) {

    // if(Globals.supermarket == null) {
    //   router.navigateByUrl('/location')
    //   return
    // }

    DB.forEach(data => {
      this.items.push({
        name: data.name[0].toUpperCase() + data.name.substr(1).toLowerCase(),
        amount: 0,
        img: data.img
      })
    })

    if(this.buyingList.length > 0 ){

      this.buyingList.forEach(item => {

        this.items.forEach(dbItem => {

          if(dbItem.name == item.name) dbItem.amount = item.amount
        })
      })
    }
  }

  get supermarket() {

    return Globals.supermarket
  }

  get itemsList() {

    return this.filteredOptions == null ? this.items : this.filteredOptions
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

  displayFn(item: ShoppingItem): string {
    return item && item.name ? item.name : '';
  }

  private _filter(name: string): ShoppingItem[] {
    const filterValue = name.toLowerCase();

    return this.items.filter(option => option.name.toLowerCase().indexOf(filterValue) === 0);
  }
  public route(){

    if(this.buyingList.length > 0)
      this.router.navigateByUrl('/compare')
  } 



  add(e?, addItem?:ShoppingItem) {

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

  remove(e?, item?:ShoppingItem) {

    if(item && item.amount > 0) item.amount -= 1
  } 

}
