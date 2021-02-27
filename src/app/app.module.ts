import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { InitComponent } from './views/init.component'
import { LocationComponent } from './views/location.component'
import { BuyingListComponent } from './views/buying-list.component'


import { SearchBarComponent } from './templates/search-bar.component';

import {MatSliderModule} from '@angular/material/slider';
import {MatButtonModule} from '@angular/material/button';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';


const routes: Routes = [
  { path: 'intro', component: InitComponent },
  { path: 'location', component: LocationComponent },
  { path: 'list', component: BuyingListComponent },
  { path: '**', redirectTo: '/intro', pathMatch: 'full' },
];


@NgModule({
  declarations: [
    AppComponent,
    InitComponent,
    LocationComponent,
    BuyingListComponent,
    SearchBarComponent,
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule,
    RouterModule.forRoot(routes),
    BrowserAnimationsModule,

    MatSliderModule,
    MatButtonModule,
    MatAutocompleteModule,
    MatFormFieldModule,
    MatInputModule 
  ],
  providers: [],
  exports: [
    RouterModule
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
