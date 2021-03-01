import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { Globals } from "../globals";
import { ItemService } from "../provider/item.service";
import { ShoppingItem } from "./shopping-item";
@Component({
  selector: "optimized",
  template: `
  

  <h4>Optimized shopping list</h4>

  <div id="buying-list-wrapper">

  <ul>
    <li *ngFor="let item of optList" (click)="toggleOpacity($event)">
      
      <div class="item-amount">{{item.name}}</div>
        
      <div>
        <img src="./assets/images/empty-image.jpg" />
      </div>

      <div class="item-amount">{{item.amount}}</div>

    </li>
  </ul>

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
      display: inline-block;
      width: 50%;
      box-sizing:border-box;
      padding: 2.5%;
      text-align:center;
      cursor:pointer;
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

    constructor(public router: Router) {

      // if(Globals.supermarket == null || Globals.shoppingList.length == 0) {
      //   router.navigateByUrl('/location')
      //   return
      // }

        this.optList = Globals.optShoppingList
    }


    toggleOpacity(e) {

      if(e.target.getAttribute('checked') == 'true') {

        e.target.style.opacity = '1'

        e.target.setAttribute('checked', 'false')
      }
      else {

        e.target.style.opacity = '.3'

        e.target.setAttribute('checked', 'true')
      }
    }
}