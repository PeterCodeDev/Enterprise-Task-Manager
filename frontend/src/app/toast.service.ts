import { Injectable } from '@angular/core';

export interface Toast {
  message: string;
  type: 'success' | 'error' | 'info';
  undoCallback?: () => void;
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  toasts: Toast[] = [];

  show(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    const toast: Toast = { message, type };
    this.toasts.push(toast);
    setTimeout(() => {
      const idx = this.toasts.indexOf(toast);
      if (idx >= 0) this.toasts.splice(idx, 1);
    }, 3500);
  }

  showUndo(message: string, onUndo: () => void): void {
    const toast: Toast = { message, type: 'info', undoCallback: onUndo };
    this.toasts.push(toast);
    setTimeout(() => {
      const idx = this.toasts.indexOf(toast);
      if (idx >= 0) this.toasts.splice(idx, 1);
    }, 5000);
  }

  remove(index: number): void {
    this.toasts.splice(index, 1);
  }
}
