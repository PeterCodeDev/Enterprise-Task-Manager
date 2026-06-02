import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private darkSubject = new BehaviorSubject<boolean>(this.getSaved());
  isDark$ = this.darkSubject.asObservable();

  private getSaved(): boolean {
    const saved = localStorage.getItem('taskmanager_theme');
    return saved === 'dark';
  }

  get isDark(): boolean {
    return this.darkSubject.value;
  }

  init(): void {
    this.apply(this.isDark);
  }

  toggle(): void {
    const next = !this.isDark;
    localStorage.setItem('taskmanager_theme', next ? 'dark' : 'light');
    this.darkSubject.next(next);
    this.apply(next);
  }

  private apply(dark: boolean): void {
    document.documentElement.setAttribute('data-theme', dark ? 'dark' : 'light');
  }
}
