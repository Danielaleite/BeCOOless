import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations'
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';
import { HttpClientModule } from '@angular/common/http';

import { InitComponent } from './views/init.component'
import { LocationComponent } from './views/location.component'
import { BuyingListComponent } from './views/buying-list.component'
import { LoginComponent } from './views/login.component'


import { SearchBarComponent } from './templates/search-bar.component';

import {MatSliderModule} from '@angular/material/slider';
import {MatButtonModule} from '@angular/material/button';
import {MatAutocompleteModule} from '@angular/material/autocomplete';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatInputModule} from '@angular/material/input';
import { ItemService } from './provider/item.service';
import { CompareComponent } from './views/compare.component';
import { OptimizedListComponent } from './views/optimized-list.component';


const routes: Routes = [
  { path: 'intro', component: InitComponent },
  { path: 'location', component: LocationComponent },
  { path: 'list', component: BuyingListComponent },
  { path: 'login', component: LoginComponent },
  { path: 'compare', component: CompareComponent },
  { path: 'optimized', component: OptimizedListComponent },
  { path: '**', redirectTo: '/intro', pathMatch: 'full' },
];


@NgModule({
  declarations: [
    AppComponent,
    InitComponent,
    LocationComponent,
    BuyingListComponent,
    SearchBarComponent,
    CompareComponent,
    LoginComponent,
    OptimizedListComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    ReactiveFormsModule,
    AppRoutingModule,
    HttpClientModule,
    RouterModule.forRoot(routes),
    BrowserAnimationsModule,

    MatSliderModule,
    MatButtonModule,
    MatAutocompleteModule,
    MatFormFieldModule,
    MatInputModule 
  ],
  providers: [ ItemService ],
  exports: [
    RouterModule
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
