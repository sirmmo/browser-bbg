import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';

declare const google: any;

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://51.15.160.236:9899/api';
  private isAuthenticatedSubject = new BehaviorSubject<boolean>(this.hasToken());
  private googleClientId: string = '';

  public isAuthenticated$ = this.isAuthenticatedSubject.asObservable();

  constructor(
    private http: HttpClient,
    private router: Router
  ) {
    // Load Google OAuth config from backend
    this.loadGoogleConfig();
  }

  private hasToken(): boolean {
    return !!localStorage.getItem('access_token');
  }

  private loadGoogleConfig(): void {
    this.http.get<any>(`${this.apiUrl}/google/config/`).subscribe({
      next: (config) => {
        this.googleClientId = config.client_id;
      },
      error: (err) => {
        console.error('Failed to load Google OAuth config:', err);
      }
    });
  }

  getGoogleClientId(): string {
    return this.googleClientId;
  }

  register(username: string, email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/register/`, { username, email, password });
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login/`, { username, password }).pipe(
      tap((response: any) => {
        localStorage.setItem('access_token', response.access);
        localStorage.setItem('refresh_token', response.refresh);
        this.isAuthenticatedSubject.next(true);
      })
    );
  }

  loginWithGoogle(credential: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/google/login/`, {
      id_token: credential
    }).pipe(
      tap((response: any) => {
        localStorage.setItem('access_token', response.tokens.access);
        localStorage.setItem('refresh_token', response.tokens.refresh);
        this.isAuthenticatedSubject.next(true);
      })
    );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.isAuthenticatedSubject.next(false);
    this.router.navigate(['/login']);
  }

  isAuthenticated(): boolean {
    return this.hasToken();
  }
}
