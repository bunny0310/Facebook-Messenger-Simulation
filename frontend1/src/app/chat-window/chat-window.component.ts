import { Component, OnInit, Input, OnChanges, SimpleChanges } from '@angular/core';
import { ChatService } from '../services/socket.service';
import { APIService } from '../services/api/api.service';
import { FormGroup, FormControl } from '@angular/forms';

@Component({
  selector: 'app-chat-window',
  templateUrl: './chat-window.component.html',
  styleUrls: ['./chat-window.component.css']
})
export class ChatWindowComponent implements OnInit, OnChanges{

  constructor(private socketService: ChatService, private apiService: APIService) { }

  // array to store all the messages
  messages = [];
  @Input() chatName; // to store the name of the recipient
  @Input() chatEmail; // to store the email of the recipient
  @Input() cid; // to store the chat id
  userOnline; // to check whether the user is online or not
  lastSeen; // to get the duration since the user was last online
  lastSeenUnits; // to get the units of the duration since the user was last online
  // form group for the send message form
  messageForm = new FormGroup({
    message: new FormControl(''),
  });
  hasSeen = false;
  userEmail = localStorage.getItem('user'); // to store the logged in user's email
  recipientTimeObject;

  ngOnInit(): void {
  }

  ngOnChanges(changes: SimpleChanges): void {
    console.log(changes);
    // receive any new messages
    this.socketService.getMessages('message').subscribe((res) => {
      this.messages.push(res);
      const recipientDate = new Date(this.recipientTimeObject.timestamp.time).getTime();
      const lastMessageDate = new Date(String(this.messages[this.messages.length - 1].createdAt)).getTime();
      console.log(this.recipientTimeObject);
      if (recipientDate >= lastMessageDate || (this.recipientTimeObject.timestamp.type === 'in')) {
        this.hasSeen = true;
      } else {
        this.hasSeen = false;
      }
    });

    // update messages
    this.apiService.getMessages(changes.cid.currentValue);
    this.apiService.getMessagesUpdated()
    .subscribe(res => {
      this.messages = res.data;
      // const nwm = {
      //   createdAt: this.messages[0].createdAt,
      //   user: this.messages[0].user,
      //   content: {newLine: true}
      // };
      // this.messages.splice(0, 0, nwm);
      for (let i = 1; i < this.messages.length; ++i) {
        const message1 = this.messages[i];
        const message2 = this.messages[i - 1];
        if ('newLine' in message1.content || 'newLine' in message2.content) {
          continue;
        }
        const Date1 = new Date(message1.createdAt);
        const Date2 = new Date(message2.createdAt);
        const diff = Math.floor(
          (Date.UTC(Date1.getFullYear(), Date1.getMonth(), Date1.getDate()) -
          Date.UTC(Date2.getFullYear(), Date2.getMonth(), Date2.getDate()) ) / (1000 * 60 * 60 * 24)
          );
        if (diff >= 1) {
          const newLineMessage = {
            createdAt: message1.createdAt,
            user: message1.user,
            content: {newLine: true}
          };
          this.messages.splice(i, 0, newLineMessage);
        }
      }
      const recipientDate = new Date(this.recipientTimeObject.timestamp.time).getTime();
      const lastMessageDate = new Date(String(this.messages[this.messages.length - 1].createdAt)).getTime();
      if (recipientDate >= lastMessageDate || (this.recipientTimeObject.timestamp.type === 'in')) {
        this.hasSeen = true;
      } else {
        this.hasSeen = false;
      }
    });

    // update the input variables
    this.chatEmail = changes.chatEmail ? changes.chatEmail.currentValue : this.chatEmail;
    this.chatName = changes.chatName ? changes.chatName.currentValue : this.chatName;
    this.cid = changes.cid.currentValue;

    // socket request for last seen and read receipts
    const body = {
      cid: changes.cid.currentValue,
      recipientEmail: changes.chatEmail.currentValue
    };
    this.socketService.sendLSRequest(JSON.stringify(body));

    this.socketService.getMessages('read-receipt').subscribe(message => {
      this.recipientTimeObject = message;
      console.log(this.recipientTimeObject);
      if (this.messages.length > 0) {
        const recipientDate = new Date(this.recipientTimeObject.timestamp.time).getTime();
        const lastMessageDate = new Date(String(this.messages[this.messages.length - 1].createdAt)).getTime();
        if (recipientDate >= lastMessageDate || (this.recipientTimeObject.timestamp.type === 'in')) {
          this.hasSeen = true;
        } else {
          this.hasSeen = false;
        }
      }
      });
   // socket call to receive the recipient's last seen information
    this.socketService.getMessages('new-message').subscribe(message => {
      const ls = new Date(message.timestamp);
      if (message.online === false) {
        this.userOnline = false;
        this.lastSeen = Math.floor(((Date.now() - ls.getTime()) / 60000));
        console.log(this.lastSeen);
        this.lastSeenUnits = (this.lastSeen === 1 ? 'minute' : 'minutes');
        if (this.lastSeen >= 60) {
          this.lastSeen = Math.floor(this.lastSeen / 60);
          this.lastSeenUnits = (this.lastSeen === 1 ? 'hour' : 'hours');
          if (this.lastSeen >= 24) {
            this.lastSeen = Math.floor(this.lastSeen / 24);
            this.lastSeenUnits = (this.lastSeen === 1 ? 'day' : 'days');
          }
        }
      }
      else {
        console.log('true online');
        this.userOnline = true;
      }
    });
  }

  // api call to send the message
  sendMessage(userEmail: string, cid: number): void {
    this.apiService.sendMessage(userEmail, this.messageForm.get('message').value, cid, this.chatEmail);
  }

  // to check whether a message is a new text message or a seperator message
  isNewLineMessage(message: any) {
    return 'newLine' in message.content;
  }

}
