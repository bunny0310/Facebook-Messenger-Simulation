import { Injectable } from '@angular/core';
import { Subject, Observable } from 'rxjs';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class APIService {
  chatsUpdated = new Subject<{data: []}>();
  chats = [];
  messagesUpdated = new Subject<{data: []}>();
  messages = [];
  constructor(private http: HttpClient) { }

  getChats(): void {
    const data = {
      email: localStorage.getItem('user')
    };
    console.log(data);
    this.http.post<[]>('http://localhost:5000/getChats', data)
      .subscribe((res: any) => {
        this.chats = res;
        this.chatsUpdated.next({data: res});
      });
  }

  getChatsUpdated(): Observable<any> {
    return this.chatsUpdated.asObservable();
  }

  getMessages(cid: number): void {
    const data = {
      cid
    };
    this.http.post<[]>('http://localhost:5000/loadMessages', data)
      .subscribe((res: any) => {
        this.messages = res;
        this.messagesUpdated.next({data: res});
      });
  }

  getMessagesUpdated(): Observable<any> {
    return this.messagesUpdated.asObservable();
  }

  sendMessage(userEmail: string, message: string, cid: number, recipientEmail: string): void {
    const data = {
      cid,
      message,
      email: userEmail,
      recipientEmail
    };

    this.http.post('http://localhost:5001/sendMessage', data)
    .subscribe((res) => {
      console.log(res);
    });
  }

  updateChatUserTimestamp(cid: number, userEmail: string) {
    const data = {
      cid,
      userEmail
    };
    this.http.post('http://localhost:5001/updateChatTimestamp', data)
    .subscribe((res) => {
      console.log(res);
    });
  }
}
