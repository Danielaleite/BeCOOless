import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { Globals } from "../globals";
import { ItemService } from "../provider/item.service";
import { ShoppingItem } from "./shopping-item";
@Component({
  selector: "optimized",
  template: `
  

  <h4>COOLess Shopping List</h4>

  <div id="buying-list-wrapper">

  <ul *ngIf="opt && normal">

    <li>
      <div class="item-amount">Item</div>
      <div class="item-amount">Quantity</div>
      <div class="item-amount">Carbon (Kg)</div>
      <div class="item-amount">Price (€)</div>
    </li>

    <li *ngFor="let item of optList" (click)="toggleOpacity($event)">
      
      <div class="item-amount">{{titleCase(item.name)}}</div>
      <div class="item-amount">{{item.amount}}</div>
      <div class="item-amount">{{item.carbon}}</div>
      <div class="item-amount">{{item.price}}</div>

    </li>

    
    <li>
      <div class="item-amount">Total</div>
      <div class="item-amount"></div>
      <div class="item-amount">{{fullCarbon}}</div>
      <div class="item-amount">{{fullPrice}}</div>
    </li>
  </ul>

</div>




<div *ngIf="opt && normal">
  <div>
    You've spent <strong>{{moneySpend}} €</strong> extra to
    save <strong style="color: #1FCC79">{{carbonSaved}} kg</strong> of CO<sub>2</sub>
  </div>
</div>

  `,
  styles: [
    `
    #buying-list-wrapper {
      margin-bottom: 100px;
    }
    
    #buying-list-wrapper ul {
    }
  
    #buying-list-wrapper ul li {
      position: relative;
      display: flex;
      justify-content: space-between;
      width: 100%;
      box-sizing:border-box;
      padding: 2.5%;
      text-align:center;
      cursor:pointer;
      border-bottom: 1px solid #777;
    }
    #buying-list-wrapper ul li:last-child {
      cursor:default;
      border: none;
    }
    #buying-list-wrapper ul li:first-child {
      cursor:default;
      font-size: 1.2rem;
    }

    #buying-list-wrapper ul li div {
      width: 20%;
      text-align:left;
    }

    #buying-list-wrapper ul li img {
      width: 100%;
    }

    #buying-list-wrapper ul li .item-bar {
  
      display: flex;
      justify-content:center;
      width: 90%;
      height: 50px;
      line-height: 50px;
    }

    #buying-list-wrapper ul li .item-bar div {

    }



  
    `,
  ],
})
export class OptimizedListComponent {

    public optList: ShoppingItem[]

    public normal: { price: number, carbon: number}
    public opt: any

    constructor(public router: Router, public itemService: ItemService) {

      if(Globals.supermarket == null) {
        router.navigateByUrl('/location')
        return
      }
      else if(Globals.shoppingList.length == 0) {
        router.navigateByUrl('/list')
        return
      }

        this.optList = Globals.optShoppingList

        this.runAlgorithm()
    }

    public get fullPrice() { return this.opt.price }
    public get fullCarbon() { return this.opt.carbon }
    public get moneySpend() { return (this.opt.price - this.normal.price).toFixed(2) }
    public get carbonSaved() { return (this.normal.carbon - this.opt.carbon).toFixed(2) }

    toggleOpacity(e) {

      let ele = e.target.closest('li')

      if(ele.getAttribute('checked') == 'true') {

        ele.style.opacity = '1'

        ele.setAttribute('checked', 'false')
      }
      else {

        ele.style.opacity = '.3'

        ele.setAttribute('checked', 'true')
      }
    }

    
  runAlgorithm() {
    
    this.itemService.getOptimalPrice().subscribe((optPrice)=> {

      this.normal = optPrice
    })

    this.itemService.getOptimalCO2().subscribe((optCO2)=> {

      this.opt = optCO2

      Globals.optPrice = optCO2.price
      Globals.optCarbon = optCO2.carbon

      let array = Object.keys(optCO2)

      array.splice(array.indexOf('price'), 1)
      array.splice(array.indexOf('carbon'), 1)

      Globals.optShoppingList = []
      
      array.forEach((a, i) => {

        Globals.optShoppingList.push({
          name: a,
          amount: optCO2[a]['amount'],
          carbon: optCO2[a]['carbon'],
          price: optCO2[a]['price']
        })
      })
    })
  }


  titleCase(str) {
    let splitStr = str.toLowerCase().split(' ');
    for (let i = 0; i < splitStr.length; i++) {
        splitStr[i] = splitStr[i].charAt(0).toUpperCase() + splitStr[i].substring(1);     
    }
    return splitStr.join(' '); 
 }
}