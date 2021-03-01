import { Component } from "@angular/core";
import { Router } from "@angular/router";
import { Globals } from "../globals";
import { ItemService } from "../provider/item.service";
@Component({
  selector: "comparison",
  template: `
  
    <div *ngIf="!optimalPrice || !optimalCO2">loading...</div>

    <div *ngIf="optimalPrice && optimalCO2" id="comparison-wrapper">
          
      <div class="col-2">
        <h4>Normal shopping</h4>
        <span class="comparison-price">{{ optimalPrice.price }} $</span>
        <div class="comparison-carbon-wrapper">
          <div class="comparison-title">Amount of CO2</div>
          <div class="comparison-carbon">{{ optimalPrice.carbon }} kg</div>
        </div>
      </div>

      <div class="col-2">
        <h4>COOLess shopping</h4>
        <span class="comparison-price green green-border">{{ optimalCO2.price }} $</span>
        <div class="comparison-carbon-wrapper green-border">
          <div class="comparison-title">Amount of CO2</div>
          <div class="comparison-carbon green">{{ optimalCO2.carbon }} kg</div>
        </div>
      </div>
    </div>

    <div class="threshold-slider">
      <h4>Threshold</h4>
      <mat-slider class="slider"
        thumbLabel  
        [displayWith]="formatLabel"
        min="1"
        max="15" (change)="setThreshold($event)" [value]="default_threshold"></mat-slider>


      <div class="btn" (click)="route()">Get List</div>

    </div>



  `,
  styles: [
    `
    .slider {

      width: 100%;
      margin-top: 20px;
    }

    #comparison-wrapper {

      display: flex;

      text-align: center;

    }

    .col-2 {
      width: 50%;
    }
    .col-2 .comparison-price {

      width: 80%;
      font-size: 1.2rem;
      font-weight:700;
      display:inline-block;
      height: 50px;
      line-height: 50px;
      border: 1px solid #333;
      border-radius: 40px 40px 40px 40px;
      margin-bottom: 20px;
    }
    .col-2 .comparison-carbon-wrapper {

      width: 80%;
      font-size: 1.2rem;
      font-weight:700;
      display:inline-block;
      height: 70px;
      line-height: 30px;
      border: 1px solid #333;
      border-radius: 10px 10px 10px 10px;
      margin-bottom: 20px;
    }
    .col-2 .comparison-title {
      width: 100%;
      height:30%;
      font-size: .8rem;
      color: #555;
    }
    .col-2 .comparison-carbon {
      width: 100%;
      height:70%;
      line-height:40px;
    }
    .col-2 .green {

      color: #1FCC79;
    }
    .col-2 .green-border {
      border: 1px solid #1FCC79;
    }

    .threshold-slider {


    }

    `,
  ],
})
export class CompareComponent {

  public optimalPrice: { price: number, co2: number }
  public optimalCO2: {}

  public default_threshold: number

  constructor(public router: Router, public itemService: ItemService) {

    Globals.optShoppingList = []

    this.threshold = this.default_threshold = 5

    this.runAlgorithm()
  }

  public get threshold() { return Globals.threshold }
  public set threshold(v: number) { Globals.threshold = v }

  public setThreshold(e) {

    this.threshold = e.value

    this.runAlgorithm()
  }

  runAlgorithm() {
    
    this.itemService.getOptimalPrice().subscribe((optPrice)=> {

      this.optimalPrice = optPrice
    })

    this.itemService.getOptimalCO2().subscribe((optCO2)=> {

      this.optimalCO2 = optCO2

      let array = Object.keys(this.optimalCO2)
      array.splice(array.indexOf('price'), 1)
      array.splice(array.indexOf('carbon'), 1)

      Globals.optShoppingList = []
      
      array.forEach((a, i) => {
        Globals.optShoppingList.push({
          name: a,
          amount: optCO2[a]
        })
      })
    })
  }

  formatLabel(value: number) {
    return value + '%';
  }
  
  public route(){

    if(Globals.optShoppingList.length > 0)
      this.router.navigateByUrl('/optimized')
  } 
}