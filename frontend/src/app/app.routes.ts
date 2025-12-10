import { Routes } from '@angular/router';
import { LoginComponent } from './components/login/login.component';
import { RegisterComponent } from './components/register/register.component';
import { BaseComponent } from './components/base/base.component';
import { PartyComponent } from './components/party/party.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'register', component: RegisterComponent },
  { path: 'base', component: BaseComponent },
  { path: 'party', component: PartyComponent },
];
