import { Component, OnInit } from '@angular/core';
import { TaskService } from './task.service';
import { Task } from './task.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  tasks: Task[] = [];
  newTitle = '';
  newDescription = '';
  loading = false;

  constructor(private taskService: TaskService) {}

  ngOnInit(): void {
    this.loadTasks();
  }

  loadTasks(): void {
    this.loading = true;
    this.taskService.getTasks().subscribe({
      next: (data) => {
        this.tasks = data;
        this.loading = false;
      },
      error: (err) => {
        console.error('Error al cargar tareas:', err);
        this.loading = false;
      },
    });
  }

  createTask(): void {
    if (!this.newTitle.trim()) return;

    this.taskService
      .createTask({
        titulo: this.newTitle.trim(),
        descripcion: this.newDescription.trim() || null,
      })
      .subscribe({
        next: (task) => {
          this.tasks.unshift(task);
          this.newTitle = '';
          this.newDescription = '';
        },
        error: (err) => console.error('Error al crear tarea:', err),
      });
  }

  toggleTask(task: Task): void {
    this.taskService.toggleTask(task.id).subscribe({
      next: (updated) => {
        const index = this.tasks.findIndex((t) => t.id === updated.id);
        if (index !== -1) {
          this.tasks[index] = updated;
        }
      },
      error: (err) => console.error('Error al actualizar tarea:', err),
    });
  }

  deleteTask(task: Task): void {
    this.taskService.deleteTask(task.id).subscribe({
      next: () => {
        this.tasks = this.tasks.filter((t) => t.id !== task.id);
      },
      error: (err) => console.error('Error al eliminar tarea:', err),
    });
  }
}
