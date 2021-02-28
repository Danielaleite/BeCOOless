import { Injectable } from "@angular/core";
import { HttpClient, HttpHeaders } from '@angular/common/http';

import { Observable, throwError } from 'rxjs';
import { catchError, retry } from 'rxjs/operators';
import { Globals } from "../globals";



@Injectable() 
export class ItemService {

    private priceUrl: string = 'https://becooless.herokuapp.com/api/prototype/2/user_test/optimal_price'
    private co2Url: string = 'https://becooless.herokuapp.com/api/prototype/2/user_test/optimal_co2'

    constructor(public http: HttpClient) {

        
    }

    getOptimalPrice() : Observable<any> {

        let list: {} = {}

        Globals.shoppingList.forEach(li => {
            list[li.name.toLowerCase()] = li.amount
        })

        const headers = new HttpHeaders({
            'Content-Type': 'application/json'
        })

        const options = {
            headers,
        }

        let body = {
            location: Globals.supermarket,
            shopping_list: list,
            cost_threshold: Globals.threshold,
            updated: 0,
            userkey: 'user_test',
            time: '2020-08-03 08:00'
        }

        return this.http.post(this.priceUrl, body, options)
    }
    
    getOptimalCO2() : Observable<any> {

        let list: {} = {}

        Globals.shoppingList.forEach(li => {
            list[li.name.toLowerCase()] = li.amount
        })

        const headers = new HttpHeaders({
            'Content-Type': 'application/json'
        })

        const options = {
            headers,
        }

        let body = {
            location: Globals.supermarket,
            shopping_list: list,
            cost_threshold: Globals.threshold,
            updated: 0,
            userkey: 'user_test',
            time: '2020-08-03 08:00'
        }

        return this.http.post(this.co2Url, body, options)
    }
}