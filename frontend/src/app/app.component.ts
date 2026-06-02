import { Component, OnInit } from '@angular/core';
import { TaskService } from './task.service';
import { AuthService } from './auth.service';
import { CategoryService } from './category.service';
import { ToastService } from './toast.service';
import { ThemeService } from './theme.service';
import { Task, Category } from './task.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  currentView: 'dashboard' | 'tasks' | 'categories' = 'dashboard';
  tasks: Task[] = [];
  categories: Category[] = [];
  newTitle = '';
  newDescription = '';
  newDueDate = '';
  newPriority = 'media';
  selectedCategoryIds: number[] = [];
  filterCategoryId: number | null = null;
  filterPriority: string | null = null;
  showVencidas = false;
  searchTerm = '';
  sortBy = 'id';
  sortOrder = 'desc';
  loading = false;

  showCreateForm = false;

  editingTaskId: number | null = null;
  editTitle = '';
  editDescription = '';
  editDueDate = '';
  editPriority = 'media';
  editCategoryIds: number[] = [];
  deleteConfirmTask: Task | null = null;
  detailTask: Task | null = null;

  showCategoryPanel = false;
  newCategoryName = '';
  newCategoryColor = '#4361ee';
  deleteConfirmCatId: number | null = null;

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
    public theme: ThemeService,
  ) {}

  ngOnInit(): void {
    this.theme.init();
    if (this.authService.hasToken()) {
      this.loadCategories();
      this.loadTasks();
    }
  }

  setView(view: 'dashboard' | 'tasks' | 'categories'): void {
    this.currentView = view;
    if (view === 'dashboard' || view === 'tasks') {
      this.loadTasks();
    }
  }

  get userEmail(): string | null {
    return this.authService.getEmail();
  }

  get stats() {
    const total = this.tasks.length;
    const completadas = this.tasks.filter((t) => t.completada).length;
    const pendientes = total - completadas;
    const vencidas = this.tasks.filter((t) => !t.completada && this.isOverdue(t)).length;
    const porcentaje = total > 0 ? Math.round((completadas / total) * 100) : 0;
    return { total, completadas, pendientes, vencidas, porcentaje };
  }

  isOverdue(task: Task): boolean {
    if (!task.fecha_vencimiento || task.completada) return false;
    return new Date(task.fecha_vencimiento) < new Date();
  }

  priorityColor(prioridad: string): string {
    if (prioridad === 'alta') return '#ef476f';
    if (prioridad === 'media') return '#ffd166';
    return '#06d6a0';
  }

  priorityLabel(prioridad: string): string {
    if (prioridad === 'alta') return 'Alta';
    if (prioridad === 'media') return 'Media';
    return 'Baja';
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
    const search = this.searchTerm.trim() || undefined;
    this.taskService.getTasks(1, 50, this.filterCategoryId ?? undefined, this.showVencidas, search, this.sortBy, this.sortOrder, this.filterPriority ?? undefined).subscribe({
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
        prioridad: this.newPriority,
        fecha_vencimiento: this.newDueDate ? new Date(this.newDueDate).toISOString() : null,
      })
      .subscribe({
        next: (task) => {
          this.tasks.unshift(task);
          this.newTitle = '';
          this.newDescription = '';
          this.newDueDate = '';
          this.newPriority = 'media';
          this.selectedCategoryIds = [];
          this.showCreateForm = false;
          this.toast.show('Tarea creada', 'success');
        },
        error: () => this.toast.show('Error al crear tarea', 'error'),
      });
  }

  startEdit(task: Task): void {
    this.editingTaskId = task.id;
    this.editTitle = task.titulo;
    this.editDescription = task.descripcion || '';
    this.editPriority = task.prioridad;
    this.editDueDate = task.fecha_vencimiento
      ? new Date(task.fecha_vencimiento).toISOString().slice(0, 10)
      : '';
    this.editCategoryIds = task.categories.map((c) => c.id);
  }

  cancelEdit(): void {
    this.editingTaskId = null;
    this.editTitle = '';
    this.editDescription = '';
    this.editDueDate = '';
    this.editCategoryIds = [];
  }

  toggleEditCategory(catId: number): void {
    const idx = this.editCategoryIds.indexOf(catId);
    if (idx >= 0) {
      this.editCategoryIds.splice(idx, 1);
    } else {
      this.editCategoryIds.push(catId);
    }
  }

  saveEdit(): void {
    if (!this.editTitle.trim() || this.editingTaskId === null) return;
    this.taskService
      .updateTask(this.editingTaskId, {
        titulo: this.editTitle.trim(),
        descripcion: this.editDescription.trim() || null,
        category_ids: this.editCategoryIds,
        prioridad: this.editPriority,
        fecha_vencimiento: this.editDueDate ? new Date(this.editDueDate).toISOString() : null,
      })
      .subscribe({
        next: (updated) => {
          const index = this.tasks.findIndex((t) => t.id === updated.id);
          if (index !== -1) {
            this.tasks[index] = updated;
          }
          this.cancelEdit();
          this.toast.show('Tarea actualizada', 'success');
        },
        error: () => this.toast.show('Error al actualizar tarea', 'error'),
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

  confirmDelete(task: Task): void {
    this.deleteConfirmTask = task;
  }

  cancelDelete(): void {
    this.deleteConfirmTask = null;
  }

  executeDelete(): void {
    if (!this.deleteConfirmTask) return;
    const task = this.deleteConfirmTask;
    this.deleteConfirmTask = null;
    this.taskService.deleteTask(task.id).subscribe({
      next: () => {
        this.tasks = this.tasks.filter((t) => t.id !== task.id);
        this.toast.show('Tarea eliminada', 'info');
      },
      error: () => this.toast.show('Error al eliminar tarea', 'error'),
    });
  }

  createCategory(): void {
    const nombre = this.newCategoryName.trim();
    if (!nombre) return;
    this.categoryService.createCategory(nombre, this.newCategoryColor).subscribe({
      next: (cat) => {
        this.categories.push(cat);
        this.newCategoryName = '';
        this.newCategoryColor = '#4361ee';
        this.toast.show('Categoría creada', 'success');
      },
      error: (err) => {
        if (err.status === 409) {
          this.toast.show('Esa categoría ya existe', 'error');
        } else {
          this.toast.show('Error al crear categoría', 'error');
        }
      },
    });
  }

  confirmDeleteCategory(catId: number): void {
    this.deleteConfirmCatId = catId;
  }

  cancelDeleteCategory(): void {
    this.deleteConfirmCatId = null;
  }

  deleteCategory(): void {
    if (this.deleteConfirmCatId === null) return;
    const catId = this.deleteConfirmCatId;
    this.deleteConfirmCatId = null;
    this.categoryService.deleteCategory(catId).subscribe({
      next: () => {
        this.categories = this.categories.filter((c) => c.id !== catId);
        this.loadTasks();
        this.toast.show('Categoría eliminada', 'info');
      },
      error: () => this.toast.show('Error al eliminar categoría', 'error'),
    });
  }

  openDetail(task: Task): void {
    this.detailTask = task;
  }

  closeDetail(): void {
    this.detailTask = null;
  }

  editFromDetail(): void {
    if (!this.detailTask) return;
    this.startEdit(this.detailTask);
    this.closeDetail();
  }

  deleteFromDetail(): void {
    if (!this.detailTask) return;
    this.confirmDelete(this.detailTask);
    this.closeDetail();
  }
}
