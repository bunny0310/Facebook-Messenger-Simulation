import { Component, OnInit } from '@angular/core';
import { FormGroup, FormControl, Validators } from '@angular/forms';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Router } from '@angular/router';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material/snack-bar';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent implements OnInit {
  loginForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.email]),
    password: new FormControl('', [Validators.required, Validators.minLength(6)])
  });
  constructor(
    private httpClient: HttpClient,
    private router: Router,
    private snackbar: MatSnackBar) { }

  ngOnInit() {
  }

  get email() {
    return this.loginForm.get('email');
  }

  onSubmit(): void {
    if (this.loginForm === null) {
      return;
    }
    if (this.loginForm.get('email') === null) {
      return;
    }
    if (this.loginForm.get('password') === null) {
      return;
    }
    const formData = {
      email: this.loginForm.get('email').value,
      password: this.loginForm.get('password').value
    };

    this.httpClient.post('http://127.0.0.1:5000/login', formData, {observe: 'response'})
    .pipe(
      catchError(this.handleError.bind(this))
    )
    .subscribe((response) => {
      // if (error.status === 401) {
      //   this.invalidLogin = true;
      // }
      const user: any = response.body;
      localStorage.setItem('user', user.email);
      this.router.navigate(['/']);
    });
  }

  private handleError(error: HttpErrorResponse) {
    if (error.status === 401) {
    }
      // The backend returned an unsuccessful response code.
      // The response body may contain clues as to what went wrong.
    // Return an observable with a user-facing error message.
    this.snackbar.open('Authorization failed. Incorrect login details', '', {
      duration: 2000
    });
    return throwError('Error!');
  }
}

