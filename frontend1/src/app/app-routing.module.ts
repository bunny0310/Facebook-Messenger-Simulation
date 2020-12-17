import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { LoggedInGuardService } from './guards/loggedInGuard';
import { AuthGuardService } from './guards/authGuard';
import { DashboardComponent } from './dashboard/dashboard.component';


const routes: Routes = [
  {path: 'login', component: LoginComponent, canActivate: [LoggedInGuardService]},
  {path: '', component: DashboardComponent, canActivate: [AuthGuardService]}
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { relativeLinkResolution: 'legacy' })],
  exports: [RouterModule]
})
export class AppRoutingModule { }
