import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { ApiService, PlayerProfile, BuildingType, Building } from '../../services/api.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-base',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './base.component.html',
  styleUrl: './base.component.css'
})
export class BaseComponent implements OnInit, OnDestroy {
  profile: PlayerProfile | null = null;
  buildingTypes: BuildingType[] = [];
  buildings: Building[] = [];
  gridSize = 10;
  grid: any[][] = [];
  selectedBuildingType: BuildingType | null = null;
  message = '';

  constructor(
    private apiService: ApiService,
    private authService: AuthService,
    private router: Router
  ) {
    this.initializeGrid();
  }

  ngOnInit(): void {
    this.loadData();
    // Start automatic resource collection every minute
    this.apiService.startAutoCollection();
  }

  ngOnDestroy(): void {
    // Stop automatic resource collection when component is destroyed
    this.apiService.stopAutoCollection();
  }

  initializeGrid(): void {
    this.grid = [];
    for (let y = 0; y < this.gridSize; y++) {
      this.grid[y] = [];
      for (let x = 0; x < this.gridSize; x++) {
        this.grid[y][x] = { x, y, building: null };
      }
    }
  }

  loadData(): void {
    this.apiService.getProfile().subscribe({
      next: (profile) => {
        this.profile = profile;
      },
      error: (err) => console.error('Error loading profile:', err)
    });

    this.apiService.getBuildingTypes().subscribe({
      next: (types) => {
        this.buildingTypes = types;
      },
      error: (err) => console.error('Error loading building types:', err)
    });

    this.apiService.getBuildings().subscribe({
      next: (buildings) => {
        this.buildings = buildings;
        this.updateGrid();
      },
      error: (err) => console.error('Error loading buildings:', err)
    });
  }

  updateGrid(): void {
    this.initializeGrid();
    this.buildings.forEach(building => {
      if (building.position_x < this.gridSize && building.position_y < this.gridSize) {
        this.grid[building.position_y][building.position_x].building = building;
      }
    });
  }

  selectBuildingType(type: BuildingType): void {
    this.selectedBuildingType = type;
    this.message = `Selected: ${type.name}. Click on grid to place.`;
  }

  placeBuilding(x: number, y: number): void {
    if (!this.selectedBuildingType) {
      this.message = 'Please select a building type first';
      return;
    }

    if (this.grid[y][x].building) {
      this.message = 'Position already occupied';
      return;
    }

    this.apiService.createBuilding({
      building_type: this.selectedBuildingType.id,
      position_x: x,
      position_y: y
    }).subscribe({
      next: (building) => {
        this.buildings.push(building);
        this.updateGrid();
        this.loadData();
        this.message = `${this.selectedBuildingType!.name} placed! Building...`;
        this.selectedBuildingType = null;
      },
      error: (err) => {
        this.message = err.error?.error || 'Failed to place building';
      }
    });
  }

  collectResources(): void {
    this.apiService.collectResources().subscribe({
      next: (response) => {
        this.message = 'Resources collected!';
        // Refresh profile to show updated resources
        this.apiService.getProfile().subscribe({
          next: (profile) => {
            this.profile = profile;
          }
        });
      },
      error: (err) => {
        this.message = 'Failed to collect resources';
      }
    });
  }

  deleteBuilding(building: Building): void {
    if (confirm('Delete this building?')) {
      this.apiService.deleteBuilding(building.id).subscribe({
        next: () => {
          this.buildings = this.buildings.filter(b => b.id !== building.id);
          this.updateGrid();
          this.message = 'Building deleted';
        },
        error: (err) => {
          this.message = 'Failed to delete building';
        }
      });
    }
  }

  logout(): void {
    this.authService.logout();
  }

  getBuildingIcon(building: Building): string {
    return building.building_type_detail?.icon || '🏠';
  }

  getBuildingStatus(building: Building): string {
    return building.is_built ? 'Built' : 'Building...';
  }
}
