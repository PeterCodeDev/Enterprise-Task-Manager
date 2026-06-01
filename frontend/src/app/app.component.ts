import { Component, OnInit } from '@angular/core';
import { TaskService } from './task.service';
import { AuthService } from './auth.service';
import { CategoryService } from './category.service';
import { ToastService } from './toast.service';
import { Task, Category } from './task.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  tasks: Task[] = [];
  categories: Category[] = [];
  newTitle = '';
  newDescription = '';
  newDueDate = '';
  selectedCategoryIds: number[] = [];
  filterCategoryId: number | null = null;
  showVencidas = false;
  loading = false;

  loginEmail = '';
  loginPassword = '';
  registerEmail = '';
  registerPassword = '';
  errorMessage = '';
  successMessage = '';
  showRegister = false;

  constructor(
    private taskService: TaskService,
    private categoryService: CategoryService,
    public authService: AuthService,
    public toast: ToastService,
  ) {}

  ngOnInit(): void {
    if (this.authService.hasToken()) {
      this.loadCategories();
      this.loadTasks();
    }
  }

  get userEmail(): string | null {
    return this.authService.getEmail();
  }

  isOverdue(task: Task): boolean {
    if (!task.fecha_vencimiento || task.completada) return false;
    return new Date(task.fecha_vencimiento) < new Date();
  }

  login(): void {
    if (!this.loginEmail || !this.loginPassword) return;
    this.errorMessage = '';
    this.authService.login(this.loginEmail, this.loginPassword).subscribe({
      next: () => {
        this.loginPassword = '';
        this.loadCategories();
        this.loadTasks();
        this.toast.show('Sesión iniciada', 'success');
      },
      error: () => {
        this.errorMessage = 'Email o contraseña incorrectos';
      },
    });
  }

  register(): void {
    if (!this.registerEmail || !this.registerPassword) return;
    if (this.registerPassword.length < 6) {
      this.errorMessage = 'La contraseña debe tener al menos 6 caracteres';
      return;
    }
    this.errorMessage = '';
    this.authService.register(this.registerEmail, this.registerPassword).subscribe({
      next: () => {
        this.successMessage = 'Registro exitoso. Inicia sesión.';
        this.showRegister = false;
        this.loginEmail = this.registerEmail;
        this.registerEmail = '';
        this.registerPassword = '';
        this.toast.show('Cuenta creada correctamente', 'success');
      },
      error: (err) => {
        if (err.status === 409) {
          this.errorMessage = 'Este email ya está registrado';
        } else {
          this.errorMessage = 'Error al registrarse';
        }
      },
    });
  }

  logout(): void {
    this.authService.logout();
    this.tasks = [];
    this.categories = [];
  }

  loadCategories(): void {
    this.categoryService.getCategories().subscribe({
      next: (data) => (this.categories = data),
      error: () => this.toast.show('Error al cargar categorías', 'error'),
    });
  }

  loadTasks(): void {
    this.loading = true;
    this.taskService.getTasks(1, 50, this.filterCategoryId ?? undefined, this.showVencidas).subscribe({
      next: (data) => {
        this.tasks = data;
        this.loading = false;
      },
      error: () => {
        this.loading = false;
        this.toast.show('Error al cargar tareas', 'error');
      },
    });
  }

  toggleCategory(catId: number): void {
    const idx = this.selectedCategoryIds.indexOf(catId);
    if (idx >= 0) {
      this.selectedCategoryIds.splice(idx, 1);
    } else {
      this.selectedCategoryIds.push(catId);
    }
  }

  createTask(): void {
    if (!this.newTitle.trim()) return;
    this.taskService
      .createTask({
        titulo: this.newTitle.trim(),
        descripcion: this.newDescription.trim() || null,
        category_ids: this.selectedCategoryIds,
        fecha_vencimiento: this.newDueDate ? new Date(this.newDueDate).toISOString() : null,
      })
      .subscribe({
        next: (task) => {
          this.tasks.unshift(task);
          this.newTitle = '';
          this.newDescription = '';
          this.newDueDate = '';
          this.selectedCategoryIds = [];
          this.toast.show('Tarea creada', 'success');
        },
        error: () => this.toast.show('Error al crear tarea', 'error'),
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
      error: () => this.toast.show('Error al actualizar tarea', 'error'),
    });
  }

  deleteTask(task: Task): void {
    this.taskService.deleteTask(task.id).subscribe({
      next: () => {
        this.tasks = this.tasks.filter((t) => t.id !== task.id);
        this.toast.show('Tarea eliminada', 'info');
      },
      error: () => this.toast.show('Error al eliminar tarea', 'error'),
    });
  }
}
