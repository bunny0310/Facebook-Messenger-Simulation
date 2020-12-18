import { Component, OnInit, ViewChildren, QueryList, ElementRef, AfterViewInit, ViewChild, Inject } from '@angular/core';
import { APIService } from '../services/api/api.service';
import { Router } from '@angular/router';
import { ChatService } from '../services/socket.service';
import {interval} from 'rxjs';
import { FormGroup, FormControl } from '@angular/forms';
import { DOCUMENT } from '@angular/common';
import { PageScrollService } from 'ngx-page-scroll-core';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  chats = []; // to store the list of chats
  currentChatId = -1; // to store the chat id
  messages = []; // to store the list of messages
  userEmail = localStorage.getItem('user'); // to store the logged in user's email
  chatSelected = false; // to check whether a chat has been selected or not
  chatName; // to store the name of the recipient
  chatEmail; // to store the email of the recipient
  prevChat = null;

  constructor(
  private apiService: APIService, private router: Router, private socketService: ChatService,
  private pageScrollService: PageScrollService,
  @Inject(DOCUMENT) private document: any
  ) { }

  ngOnInit(): void {
    // initiate the socket connection to store the session id
    this.socketService.sendSessionId(this.userEmail);
    // api calls to get the list of all the chats
    this.apiService.getChats();
    this.apiService.getChatsUpdated()
    .subscribe(res => {
      this.chats = res.data;
    });
    // initiate the socket connection to begin monitoring the heartbeat of the logged in user
    this.socketService.intializeSocket(this.userEmail);
  }

  // logout method
  logout(): void {
    localStorage.removeItem('user');
    this.router.navigate(['/login'])
    .then(() => {
      window.location.reload();
    });
  }

  // to set all the chat related variables
  initializeChat(cid: number, recipientName: string, recipientEmail: string): void {
    this.currentChatId = cid;
    this.chatName = recipientName;
    this.chatEmail = recipientEmail;

    this.socketService.sendClosePreviousChatSocketConnectionRequest();
    this.chatSelected = true;

    if (this.prevChat !== null) {
      this.apiService.updateChatUserTimestamp(this.prevChat, this.userEmail, 'out');
    }
    this.apiService.updateChatUserTimestamp(cid, this.userEmail, 'in');

    this.prevChat = cid;
  }

}
