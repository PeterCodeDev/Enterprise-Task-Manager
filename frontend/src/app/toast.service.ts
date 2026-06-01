import { Injectable } from '@angular/core';

export interface Toast {
  message: string;
  type: 'success' | 'error' | 'info';
}

@Injectable({ providedIn: 'root' })
export class ToastService {
  toasts: Toast[] = [];

  show(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    this.toasts.push({ message, type });
    const toast = this.toasts[this.toasts.length - 1];
    setTimeout(() => {
      const idx = this.toasts.indexOf(toast);
      if (idx >= 0) {
        this.toasts.splice(idx, 1);
      }
    }, 3500);
  }

  remove(index: number): void {
    this.toasts.splice(index, 1);
  }
}
