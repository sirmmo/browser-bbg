import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, Subject } from 'rxjs';
import { switchMap, takeUntil } from 'rxjs/operators';
import { environment } from '../../environments/environment';

export interface PlayerProfile {
  id: number;
  user: { id: number; username: string; email: string };
  party: any;
  coins: number;
  wood: number;
  stone: number;
  food: number;
  level: number;
  experience: number;
  next_level_xp: number;
  waves_survived: number;
  last_collection: string;
  created_at: string;
}

export interface BuildingType {
  id: number;
  name: string;
  description: string;
  resource_type: string;
  production_rate: number;
  cost_coins: number;
  cost_wood: number;
  cost_stone: number;
  cost_food: number;
  build_time: number;
  width: number;
  height: number;
  icon: string;
}

export interface Building {
  id: number;
  building_type: number;
  building_type_detail: BuildingType;
  position_x: number;
  position_y: number;
  is_built: boolean;
  build_started: string;
  build_completed: string | null;
  created_at: string;
}

export interface Party {
  id: number;
  name: string;
  code: string;
  created_at: string;
  is_active: boolean;
  member_count: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private apiUrl = environment.apiUrl;
  private autoCollectInterval$ = new Subject<void>();
  private isAutoCollecting = false;

  constructor(private http: HttpClient) { }

  // Profile
  getProfile(): Observable<PlayerProfile> {
    return this.http.get<PlayerProfile>(`${this.apiUrl}/profile/me/`);
  }

  collectResources(): Observable<any> {
    return this.http.post(`${this.apiUrl}/profile/collect/`, {});
  }

  // Building Types
  getBuildingTypes(): Observable<BuildingType[]> {
    return this.http.get<BuildingType[]>(`${this.apiUrl}/building-types/`);
  }

  // Buildings
  getBuildings(): Observable<Building[]> {
    return this.http.get<Building[]>(`${this.apiUrl}/buildings/`);
  }

  createBuilding(data: { building_type: number; position_x: number; position_y: number }): Observable<Building> {
    return this.http.post<Building>(`${this.apiUrl}/buildings/`, data);
  }

  checkBuildingCompletion(buildingId: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/buildings/${buildingId}/check_completion/`, {});
  }

  deleteBuilding(buildingId: number): Observable<any> {
    return this.http.delete(`${this.apiUrl}/buildings/${buildingId}/`);
  }

  // Parties
  getParties(): Observable<Party[]> {
    return this.http.get<Party[]>(`${this.apiUrl}/parties/`);
  }

  createParty(name: string): Observable<Party> {
    return this.http.post<Party>(`${this.apiUrl}/parties/`, { name });
  }

  joinParty(code: string): Observable<Party> {
    return this.http.post<Party>(`${this.apiUrl}/parties/join/`, { code });
  }

  leaveParty(): Observable<any> {
    return this.http.post(`${this.apiUrl}/parties/leave/`, {});
  }

  getPartyMembers(partyId: number): Observable<PlayerProfile[]> {
    return this.http.get<PlayerProfile[]>(`${this.apiUrl}/parties/${partyId}/members/`);
  }

  getPartyMessages(partyId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/parties/${partyId}/messages/`);
  }

  sendPartyMessage(partyId: number, message: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/parties/${partyId}/send_message/`, { message });
  }

  // Auto-collection feature
  startAutoCollection(): void {
    if (this.isAutoCollecting) {
      return; // Already collecting
    }

    this.isAutoCollecting = true;

    // Collect resources every 60 seconds (1 minute)
    interval(60000)
      .pipe(
        takeUntil(this.autoCollectInterval$),
        switchMap(() => this.collectResources())
      )
      .subscribe({
        next: (response) => {
          console.log('Auto-collected resources:', response);
        },
        error: (error) => {
          console.error('Auto-collection error:', error);
        }
      });
  }

  stopAutoCollection(): void {
    this.isAutoCollecting = false;
    this.autoCollectInterval$.next();
  }

  isCollecting(): boolean {
    return this.isAutoCollecting;
  }
}
