import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, TaskCreate } from './task.model';

@Injectable({
  providedIn: 'root',
})
export class TaskService {
  private apiUrl = 'http://localhost:8000/api/tasks';

  constructor(private http: HttpClient) {}

  getTasks(): Observable<Task[]> {
    return this.http.get<Task[]>(this.apiUrl);
  }

  createTask(task: TaskCreate): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, task);
  }

  toggleTask(taskId: number): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/${taskId}/toggle`, {});
  }

  deleteTask(taskId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${taskId}`);
  }
}
