import { Injectable } from "@angular/core";



@Injectable() 
export class ItemService {


    constructor() {

        
    }


    query(search: string) {
        console.log('QUERY', search)
        return 
    }
}