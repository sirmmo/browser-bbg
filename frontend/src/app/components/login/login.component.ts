import { Component, OnInit, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

declare const google: any;

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit, AfterViewInit {
  username = '';
  password = '';
  error = '';
  isLoading = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) { }

  ngOnInit(): void {
    // Check if user is already authenticated
    if (this.authService.isAuthenticated()) {
      this.router.navigate(['/base']);
    }
  }

  ngAfterViewInit(): void {
    // Initialize Google Sign-In after view is loaded
    this.initializeGoogleSignIn();
  }

  initializeGoogleSignIn(): void {
    // Wait for Google library to load
    const checkGoogle = setInterval(() => {
      if (typeof google !== 'undefined' && this.authService.getGoogleClientId()) {
        clearInterval(checkGoogle);
        this.renderGoogleButton();
      }
    }, 100);

    // Clear interval after 5 seconds to avoid infinite loop
    setTimeout(() => clearInterval(checkGoogle), 5000);
  }

  renderGoogleButton(): void {
    const clientId = this.authService.getGoogleClientId();
    if (!clientId) {
      console.error('Google Client ID not available');
      return;
    }

    google.accounts.id.initialize({
      client_id: clientId,
      callback: this.handleGoogleSignIn.bind(this)
    });

    google.accounts.id.renderButton(
      document.getElementById('google-signin-button'),
      {
        theme: 'outline',
        size: 'large',
        width: 300,
        text: 'signin_with'
      }
    );
  }

  handleGoogleSignIn(response: any): void {
    this.isLoading = true;
    this.error = '';

    this.authService.loginWithGoogle(response.credential).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/base']);
      },
      error: (err) => {
        this.isLoading = false;
        this.error = 'Google authentication failed. Please try again.';
        console.error('Google login error:', err);
      }
    });
  }

  login(): void {
    this.error = '';
    this.isLoading = true;

    this.authService.login(this.username, this.password).subscribe({
      next: () => {
        this.isLoading = false;
        this.router.navigate(['/base']);
      },
      error: (err) => {
        this.isLoading = false;
        this.error = 'Invalid username or password';
        console.error(err);
      }
    });
  }
}
