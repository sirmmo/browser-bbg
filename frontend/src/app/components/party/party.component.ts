import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { ApiService, PlayerProfile, Party } from '../../services/api.service';

@Component({
  selector: 'app-party',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './party.component.html',
  styleUrl: './party.component.css'
})
export class PartyComponent implements OnInit {
  profile: PlayerProfile | null = null;
  parties: Party[] = [];
  members: PlayerProfile[] = [];
  messages: any[] = [];
  newPartyName = '';
  joinCode = '';
  newMessage = '';
  message = '';

  constructor(
    private apiService: ApiService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.loadProfile();
    this.loadParties();
  }

  loadProfile(): void {
    this.apiService.getProfile().subscribe({
      next: (profile) => {
        this.profile = profile;
        if (profile.party) {
          this.loadPartyDetails(profile.party.id);
        }
      }
    });
  }

  loadParties(): void {
    this.apiService.getParties().subscribe({
      next: (parties) => {
        this.parties = parties;
      }
    });
  }

  loadPartyDetails(partyId: number): void {
    this.apiService.getPartyMembers(partyId).subscribe({
      next: (members) => {
        this.members = members;
      }
    });

    this.apiService.getPartyMessages(partyId).subscribe({
      next: (messages) => {
        this.messages = messages;
      }
    });
  }

  createParty(): void {
    if (!this.newPartyName) return;

    this.apiService.createParty(this.newPartyName).subscribe({
      next: (party) => {
        this.message = `Party created! Code: ${party.code}`;
        this.newPartyName = '';
        this.loadProfile();
        this.loadParties();
      },
      error: (err) => {
        this.message = 'Failed to create party';
      }
    });
  }

  joinParty(): void {
    if (!this.joinCode) return;

    this.apiService.joinParty(this.joinCode).subscribe({
      next: () => {
        this.message = 'Joined party successfully!';
        this.joinCode = '';
        this.loadProfile();
      },
      error: (err) => {
        this.message = 'Failed to join party';
      }
    });
  }

  leaveParty(): void {
    if (confirm('Leave this party?')) {
      this.apiService.leaveParty().subscribe({
        next: () => {
          this.message = 'Left party';
          this.members = [];
          this.messages = [];
          this.loadProfile();
        }
      });
    }
  }

  sendMessage(): void {
    if (!this.newMessage || !this.profile?.party) return;

    this.apiService.sendPartyMessage(this.profile.party.id, this.newMessage).subscribe({
      next: () => {
        this.newMessage = '';
        this.loadPartyDetails(this.profile!.party!.id);
      }
    });
  }

  goToBase(): void {
    this.router.navigate(['/base']);
  }
}
