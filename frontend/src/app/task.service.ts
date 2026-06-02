import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Task, TaskCreate } from './task.model';

@Injectable({ providedIn: 'root' })
export class TaskService {
  private apiUrl = 'http://localhost:8000/api/tasks';

  constructor(private http: HttpClient) {}

  getTasks(page: number = 1, pageSize: number = 50, categoryId?: number, vencidas?: boolean, search?: string, sortBy?: string, sortOrder?: string, prioridad?: string): Observable<Task[]> {
    let params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString())
      .set('sort_by', sortBy || 'id')
      .set('sort_order', sortOrder || 'desc');
    if (categoryId) {
      params = params.set('category_id', categoryId.toString());
    }
    if (vencidas) {
      params = params.set('vencidas', 'true');
    }
    if (search) {
      params = params.set('search', search);
    }
    if (prioridad) {
      params = params.set('prioridad', prioridad);
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
