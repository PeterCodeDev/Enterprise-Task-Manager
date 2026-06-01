import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, TaskCreate } from './task.model';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private apiUrl = 'http://localhost:8000/api/tasks';

  constructor(private http: HttpClient) {}

  getTasks(page: number = 1, pageSize: number = 20, categoryId?: number): Observable<Task[]> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    if (categoryId) {
      params = params.set('category_id', categoryId.toString());
    }
    return this.http.get<Task[]>(this.apiUrl, { params });
  }

  createTask(task: TaskCreate): Observable<Task> {
    return this.http.post<Task>(this.apiUrl, task);
  }

  updateTask(taskId: number, task: TaskCreate): Observable<Task> {
    return this.http.put<Task>(`${this.apiUrl}/${taskId}`, task);
  }

  toggleTask(taskId: number): Observable<Task> {
    return this.http.patch<Task>(`${this.apiUrl}/${taskId}/toggle`, {});
  }

  deleteTask(taskId: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${taskId}`);
  }
}
