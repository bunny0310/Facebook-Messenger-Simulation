import { Injectable } from '@angular/core';
import { Socket } from 'ngx-socket-io';
import { Observable } from 'rxjs';
import { THIS_EXPR } from '@angular/compiler/src/output/output_ast';

@Injectable({
  providedIn: 'root'
})
export class ChatService{
  constructor(private socket: Socket) {
  }
  public intializeSocket(email: string) {
    this.sendHeartbeat('connected-' + email);
  }
  public sendMessage(message: any): void {
    this.socket.emit('message', message);
  }

  public sendSessionId(email) {
    this.socket.emit('store-session', email);
  }

  public sendHeartbeat(message: any): void {
    this.socket.emit('heartbeat', message);
  }

  public sendLSRequest(message: any): void {
    this.socket.emit('lastSeen' , message);
  }

  public sendClosePreviousChatSocketConnectionRequest(): void {
    this.socket.emit('closePrevChat', '');
  }

  public getMessages = (key: string) => {
    return Observable.create((observer: any) => {
            this.socket.on(key, (message: any) => {
                observer.next(message);
            });
    });
}

}
