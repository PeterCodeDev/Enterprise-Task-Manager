import { Component, OnInit, HostListener } from '@angular/core';
import { TaskService } from './task.service';
import { AuthService } from './auth.service';
import { CategoryService } from './category.service';
import { ToastService } from './toast.service';
import { ThemeService } from './theme.service';
import { Task, Category, Subtask, Attachment, Comment } from './task.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
})
export class AppComponent implements OnInit {
  currentView: 'dashboard' | 'tasks' | 'categories' | 'calendar' | 'kanban' = 'dashboard';
  tasks: Task[] = [];
  categories: Category[] = [];
  newTitle = '';
  newDescription = '';
  newDueDate = '';
  newPriority = 'media';
  newEstado = 'pendiente';
  newRecurrencia = '';
  selectedCategoryIds: number[] = [];
  filterCategoryId: number | null = null;
  filterPriority: string | null = null;
  filterCompletada: boolean | null = null;
  showVencidas = false;
  searchTerm = '';
  sortBy = 'id';
  sortOrder = 'desc';
  loading = false;

  showCreateForm = false;
  selectedTaskIds: number[] = [];
  newSubtaskText = '';

  editingTaskId: number | null = null;
  editTitle = '';
  editDescription = '';
  editDueDate = '';
  editPriority = 'media';
  editEstado = 'pendiente';
  editRecurrencia = '';
  editCategoryIds: number[] = [];
  deleteConfirmTask: Task | null = null;
  detailTask: Task | null = null;

  newCommentText = '';
  showShortcuts = false;
  showTokensPanel = false;
  tokens: any[] = [];
  newTokenName = '';
  newTokenResult = '';

  savedFilters: { name: string; filters: any }[] = [];
  filterNameInput = '';

  reminderMinutes: number | null = null;

  showCategoryPanel = false;
  newCategoryName = '';
  newCategoryColor = '#4361ee';
  deleteConfirmCatId: number | null = null;

  showPasswordPanel = false;
  oldPassword = '';
  newPassword = '';

  showProfilePanel = false;
  profileNombre = '';
  profileBio = '';
  profileColor = '#4361ee';

  undoDeleteTimer: ReturnType<typeof setTimeout> | null = null;
  undoDeleteTask: Task | null = null;

  loginEmail = '';
  loginPassword = '';
  registerEmail = '';
  registerPassword = '';
  errorMessage = '';
  successMessage = '';
  showRegister = false;

  constructor(
    public taskService: TaskService,
    private categoryService: CategoryService,
    public authService: AuthService,
    public toast: ToastService,
    public theme: ThemeService,
  ) {}

  ngOnInit(): void {
    this.theme.init();
    const saved = localStorage.getItem('taskmanager_saved_filters');
    if (saved) this.savedFilters = JSON.parse(saved);
    if (this.authService.hasToken()) {
      this.loadCategories();
      this.loadTasks();
    }
    setInterval(() => this.checkReminders(), 30000);
  }

  setView(view: 'dashboard' | 'tasks' | 'categories' | 'calendar' | 'kanban'): void {
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

    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    const finSemana = new Date(hoy);
    finSemana.setDate(finSemana.getDate() + (7 - finSemana.getDay()));

    const tareasHoy = this.tasks.filter((t) => {
      if (!t.fecha_vencimiento || t.completada) return false;
      const fecha = new Date(t.fecha_vencimiento);
      fecha.setHours(0, 0, 0, 0);
      return fecha.getTime() === hoy.getTime();
    });

    const tareasSemana = this.tasks.filter((t) => {
      if (!t.fecha_vencimiento || t.completada) return false;
      const fecha = new Date(t.fecha_vencimiento);
      fecha.setHours(0, 0, 0, 0);
      return fecha >= hoy && fecha <= finSemana;
    });

    return { total, completadas, pendientes, vencidas, porcentaje, tareasHoy, tareasSemana };
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

  estadoColor(estado: string): string {
    const colors: Record<string, string> = {
      pendiente: '#6c757d',
      en_progreso: '#4361ee',
      completada: '#06d6a0',
      bloqueada: '#ef476f',
      en_revision: '#ffd166',
    };
    return colors[estado] || '#6c757d';
  }

  estadoLabel(estado: string): string {
    const labels: Record<string, string> = {
      pendiente: 'Pendiente',
      en_progreso: 'En progreso',
      completada: 'Completada',
      bloqueada: 'Bloqueada',
      en_revision: 'En revisión',
    };
    return labels[estado] || estado;
  }

  fechaRelativa(fecha: string | null): string {
    if (!fecha) return '';
    const ahora = new Date();
    const f = new Date(fecha);
    const diff = Math.round((f.getTime() - ahora.getTime()) / (1000 * 60 * 60 * 24));
    if (diff === 0) return 'Hoy';
    if (diff === 1) return 'Mañana';
    if (diff === -1) return 'Ayer';
    if (diff < 0) return `Hace ${Math.abs(diff)} días`;
    if (diff <= 7) return `En ${diff} días`;
    return '';
  }

  subtaskProgress(task: Task): string {
    if (!task.subtasks || task.subtasks.length === 0) return '';
    const done = task.subtasks.filter((s) => s.completada).length;
    return `${done}/${task.subtasks.length}`;
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
    this.taskService.getTasks(1, 50, this.filterCategoryId ?? undefined, this.showVencidas, search, this.sortBy, this.sortOrder, this.filterPriority ?? undefined, this.filterCompletada ?? undefined).subscribe({
      next: (data) => {
        this.tasks = data;
        this.loading = false;
        this.checkNotifications();
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
        estado: this.newEstado,
        recurrencia: this.newRecurrencia || null,
        fecha_vencimiento: this.newDueDate ? new Date(this.newDueDate).toISOString() : null,
      })
      .subscribe({
        next: (task) => {
          this.tasks.unshift(task);
          this.newTitle = '';
          this.newDescription = '';
          this.newDueDate = '';
          this.newPriority = 'media';
          this.newEstado = 'pendiente';
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
    this.editEstado = task.estado;
    this.editRecurrencia = task.recurrencia || '';
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
        estado: this.editEstado,
        recurrencia: this.editRecurrencia || null,
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
    this.undoDeleteTask = task;
    this.tasks = this.tasks.filter((t) => t.id !== task.id);
    this.toast.showUndo('Tarea eliminada', () => {
      this.tasks = [task, ...this.tasks];
      this.undoDeleteTask = null;
      this.toast.show('Eliminación deshecha', 'info');
    });
    this.undoDeleteTimer = setTimeout(() => {
      this.taskService.deleteTask(task.id).subscribe({
        error: () => this.toast.show('Error al eliminar tarea', 'error'),
      });
      this.undoDeleteTask = null;
    }, 5000);
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

  changePassword(): void {
    if (!this.oldPassword || !this.newPassword) return;
    if (this.newPassword.length < 6) {
      this.toast.show('La contraseña debe tener al menos 6 caracteres', 'error');
      return;
    }
    this.authService.changePassword(this.oldPassword, this.newPassword).subscribe({
      next: () => {
        this.oldPassword = '';
        this.newPassword = '';
        this.showPasswordPanel = false;
        this.toast.show('Contraseña cambiada', 'success');
      },
      error: (err) => {
        if (err.status === 400) {
          this.toast.show('Contraseña actual incorrecta', 'error');
        } else {
          this.toast.show('Error al cambiar contraseña', 'error');
        }
      },
    });
  }

  toggleSelect(taskId: number): void {
    const idx = this.selectedTaskIds.indexOf(taskId);
    if (idx >= 0) {
      this.selectedTaskIds.splice(idx, 1);
    } else {
      this.selectedTaskIds.push(taskId);
    }
  }

  toggleSelectAll(): void {
    if (this.selectedTaskIds.length === this.tasks.length) {
      this.selectedTaskIds = [];
    } else {
      this.selectedTaskIds = this.tasks.map((t) => t.id);
    }
  }

  batchToggle(): void {
    this.selectedTaskIds.forEach((id) => {
      this.taskService.toggleTask(id).subscribe({
        next: (updated) => {
          const idx = this.tasks.findIndex((t) => t.id === updated.id);
          if (idx !== -1) this.tasks[idx] = updated;
        },
      });
    });
    this.selectedTaskIds = [];
    this.toast.show('Tareas actualizadas', 'success');
  }

  batchDelete(): void {
    this.selectedTaskIds.forEach((id) => {
      this.taskService.deleteTask(id).subscribe({
        next: () => { this.tasks = this.tasks.filter((t) => t.id !== id); },
      });
    });
    this.selectedTaskIds = [];
    this.toast.show('Tareas eliminadas', 'info');
  }

  exportCsv(): void {
    this.taskService.exportCsv().subscribe((blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'tareas.csv';
      a.click();
      window.URL.revokeObjectURL(url);
      this.toast.show('CSV descargado', 'success');
    });
  }

  addSubtask(task: Task): void {
    if (!this.newSubtaskText.trim()) return;
    this.taskService.createSubtask(task.id, this.newSubtaskText.trim()).subscribe({
      next: (sub) => {
        task.subtasks.push(sub);
        this.newSubtaskText = '';
      },
      error: () => this.toast.show('Error al crear subtarea', 'error'),
    });
  }

  toggleSubtask(sub: import('./task.model').Subtask, task: Task): void {
    this.taskService.toggleSubtask(sub.id).subscribe({
      next: (updated) => {
        const idx = task.subtasks.findIndex((s) => s.id === updated.id);
        if (idx !== -1) task.subtasks[idx] = updated;
      },
    });
  }

  deleteSubtask(sub: import('./task.model').Subtask, task: Task): void {
    this.taskService.deleteSubtask(sub.id).subscribe({
      next: () => {
        task.subtasks = task.subtasks.filter((s) => s.id !== sub.id);
      },
    });
  }

  get calendarDate(): Date {
    return new Date();
  }

  get calendarDays(): { date: Date; tasks: Task[]; today: boolean; otherMonth: boolean }[] {
    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const startPad = firstDay.getDay() === 0 ? 6 : firstDay.getDay() - 1;
    const days: { date: Date; tasks: Task[]; today: boolean; otherMonth: boolean }[] = [];

    for (let i = startPad; i > 0; i--) {
      const d = new Date(year, month, 1 - i);
      days.push({ date: d, tasks: this.tasksForDate(d), today: false, otherMonth: true });
    }
    for (let d = 1; d <= lastDay.getDate(); d++) {
      const date = new Date(year, month, d);
      const today = date.toDateString() === now.toDateString();
      days.push({ date, tasks: this.tasksForDate(date), today, otherMonth: false });
    }
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      const d = new Date(year, month + 1, i);
      days.push({ date: d, tasks: this.tasksForDate(d), today: false, otherMonth: true });
    }
    return days;
  }

  private tasksForDate(date: Date): Task[] {
    return this.tasks.filter((t) => {
      if (!t.fecha_vencimiento) return false;
      const fd = new Date(t.fecha_vencimiento);
      return fd.getFullYear() === date.getFullYear() &&
        fd.getMonth() === date.getMonth() &&
        fd.getDate() === date.getDate();
    });
  }

  calendarMonthLabel(): string {
    const now = new Date();
    return now.toLocaleDateString('es', { month: 'long', year: 'numeric' });
  }

  onDragStart(event: DragEvent, task: Task): void {
    event.dataTransfer?.setData('text/plain', task.id.toString());
  }

  onDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  onDrop(event: DragEvent, targetTask: Task): void {
    event.preventDefault();
    const taskId = parseInt(event.dataTransfer?.getData('text/plain') || '', 10);
    if (!taskId || taskId === targetTask.id) return;
    const fromIdx = this.tasks.findIndex((t) => t.id === taskId);
    const toIdx = this.tasks.findIndex((t) => t.id === targetTask.id);
    if (fromIdx === -1 || toIdx === -1) return;
    const [moved] = this.tasks.splice(fromIdx, 1);
    this.tasks.splice(toIdx, 0, moved);
    this.toast.show('Tarea reordenada', 'info');
  }

  kanbanColumns = ['pendiente', 'en_progreso', 'bloqueada', 'en_revision', 'completada'];

  kanbanTasks(estado: string): Task[] {
    return this.tasks.filter((t) => t.estado === estado);
  }

  onKanbanDragStart(event: DragEvent, task: Task): void {
    event.dataTransfer?.setData('text/plain', task.id.toString());
  }

  onKanbanDrop(event: DragEvent, estado: string): void {
    event.preventDefault();
    const taskId = parseInt(event.dataTransfer?.getData('text/plain') || '', 10);
    const task = this.tasks.find((t) => t.id === taskId);
    if (!task || task.estado === estado) return;
    task.estado = estado;
    task.completada = estado === 'completada';
    this.taskService.updateTask(taskId, {
      titulo: task.titulo,
      descripcion: task.descripcion,
      category_ids: task.categories.map((c) => c.id),
      prioridad: task.prioridad,
      estado: estado,
      recurrencia: task.recurrencia,
      fecha_vencimiento: task.fecha_vencimiento,
    }).subscribe({
      next: (updated) => {
        const idx = this.tasks.findIndex((t) => t.id === updated.id);
        if (idx !== -1) this.tasks[idx] = updated;
        this.toast.show(`Movida a ${this.estadoLabel(estado)}`, 'info');
      },
      error: () => this.toast.show('Error al mover tarea', 'error'),
    });
  }

  onKanbanDragOver(event: DragEvent): void {
    event.preventDefault();
  }

  uploadFile(task: Task, fileInput: HTMLInputElement): void {
    const file = fileInput.files?.[0];
    if (!file) return;
    this.taskService.uploadAttachment(task.id, file).subscribe({
      next: (att) => {
        task.attachments.push(att);
        this.toast.show('Archivo subido', 'success');
      },
      error: () => this.toast.show('Error al subir archivo', 'error'),
    });
    fileInput.value = '';
  }

  deleteAttachment(att: Attachment, task: Task): void {
    this.taskService.deleteAttachment(att.id).subscribe({
      next: () => {
        task.attachments = task.attachments.filter((a) => a.id !== att.id);
        this.toast.show('Archivo eliminado', 'info');
      },
      error: () => this.toast.show('Error al eliminar archivo', 'error'),
    });
  }

  openProfile(): void {
    this.showProfilePanel = true;
    this.authService.getProfile().subscribe({
      next: (user) => {
        this.profileNombre = user.nombre || '';
        this.profileBio = user.bio || '';
        this.profileColor = user.avatar_color;
      },
    });
  }

  saveProfile(): void {
    this.authService.updateProfile({
      nombre: this.profileNombre.trim() || undefined,
      bio: this.profileBio.trim() || undefined,
      avatar_color: this.profileColor,
    }).subscribe({
      next: () => {
        this.showProfilePanel = false;
        this.toast.show('Perfil actualizado', 'success');
      },
      error: () => this.toast.show('Error al actualizar perfil', 'error'),
    });
  }

  importCsv(fileInput: HTMLInputElement): void {
    const file = fileInput.files?.[0];
    if (!file) return;
    this.taskService.importCsv(file).subscribe({
      next: (res) => {
        this.toast.show(`${res.imported} tareas importadas`, 'success');
        this.loadTasks();
      },
      error: () => this.toast.show('Error al importar CSV', 'error'),
    });
    fileInput.value = '';
  }

  copyIcalUrl(): void {
    navigator.clipboard.writeText(this.taskService.getIcalUrl()).then(() => {
      this.toast.show('URL del calendario copiada. Pégala en Google Calendar → Añadir por URL', 'info');
    });
  }

  openDetailAndLoadComments(task: Task): void {
    this.openDetail(task);
    this.taskService.getComments(task.id).subscribe({
      next: (comments) => { task.comments = comments; },
    });
    this.loadActivity(task);
  }

  addComment(task: Task): void {
    if (!this.newCommentText.trim()) return;
    this.taskService.createComment(task.id, this.newCommentText.trim()).subscribe({
      next: (comment) => {
        task.comments.push(comment);
        this.newCommentText = '';
      },
      error: () => this.toast.show('Error al añadir comentario', 'error'),
    });
  }

  deleteComment(comment: Comment, task: Task): void {
    this.taskService.deleteComment(comment.id).subscribe({
      next: () => {
        task.comments = task.comments.filter((c) => c.id !== comment.id);
      },
    });
  }

  exportBackup(): void {
    this.taskService.exportBackup().subscribe((data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'backup-etm.json'; a.click();
      window.URL.revokeObjectURL(url);
      this.toast.show('Backup exportado', 'success');
    });
  }

  importBackup(fileInput: HTMLInputElement): void {
    const file = fileInput.files?.[0];
    if (!file) return;
    this.taskService.importBackup(file).subscribe({
      next: (res) => {
        this.toast.show(`${res.imported} tareas restauradas`, 'success');
        this.loadTasks();
      },
      error: () => this.toast.show('Error al importar backup', 'error'),
    });
    fileInput.value = '';
  }

  @HostListener('document:keydown', ['$event'])
  handleKeyboard(event: KeyboardEvent): void {
    if ((event.target as HTMLElement).tagName === 'INPUT' || (event.target as HTMLElement).tagName === 'TEXTAREA' || (event.target as HTMLElement).tagName === 'SELECT') {
      if (event.key === 'Escape') (event.target as HTMLElement).blur();
      return;
    }
    if (this.currentView !== 'tasks' && this.currentView !== 'kanban') return;
    switch (event.key) {
      case 'n': this.setView('tasks'); this.showCreateForm = true; break;
      case '/': this.setView('tasks'); setTimeout(() => document.querySelector<HTMLInputElement>('.search-input')?.focus(), 100); break;
      case 'Escape': this.showCreateForm = false; this.closeDetail(); this.cancelEdit(); break;
      case '?': this.showShortcuts = !this.showShortcuts; break;
    }
  }

  checkNotifications(): void {
    if (!('Notification' in window)) return;
    if (Notification.permission === 'default') {
      Notification.requestPermission();
    }
    if (Notification.permission !== 'granted') return;
    const overdue = this.tasks.filter((t) => !t.completada && this.isOverdue(t));
    const today = this.tasks.filter((t) => {
      if (!t.fecha_vencimiento || t.completada) return false;
      return new Date(t.fecha_vencimiento).toDateString() === new Date().toDateString();
    });
    if (overdue.length > 0) {
      new Notification(`${overdue.length} tareas vencidas`, { body: overdue.map((t) => t.titulo).join(', '), icon: '/assets/icon-192.svg' });
    }
    if (today.length > 0) {
      new Notification(`${today.length} tareas para hoy`, { body: today.map((t) => t.titulo).join(', '), icon: '/assets/icon-192.svg' });
    }
  }

  formatTime(seconds: number): string {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    return h > 0 ? `${h}h ${m}m` : `${m}m`;
  }

  startTimer(task: Task): void {
    this.taskService.startTimer(task.id).subscribe();
  }

  stopTimer(task: Task): void {
    this.taskService.stopTimer(task.id).subscribe({
      next: (updated) => {
        task.tiempo_acumulado = updated.tiempo_acumulado;
        this.toast.show('Temporizador: +1 min', 'info');
      },
    });
  }

  loadActivity(task: Task): void {
    this.taskService.getActivity(task.id).subscribe({
      next: (logs) => { task.activity_logs = logs; },
    });
  }

  saveFilter(): void {
    if (!this.filterNameInput.trim()) return;
    this.savedFilters.push({
      name: this.filterNameInput.trim(),
      filters: {
        filterCategoryId: this.filterCategoryId,
        filterPriority: this.filterPriority,
        filterCompletada: this.filterCompletada,
        showVencidas: this.showVencidas,
        searchTerm: this.searchTerm,
      },
    });
    localStorage.setItem('taskmanager_saved_filters', JSON.stringify(this.savedFilters));
    this.filterNameInput = '';
    this.toast.show('Filtro guardado', 'success');
  }

  applyFilter(f: { name: string; filters: any }): void {
    this.filterCategoryId = f.filters.filterCategoryId;
    this.filterPriority = f.filters.filterPriority;
    this.filterCompletada = f.filters.filterCompletada;
    this.showVencidas = f.filters.showVencidas;
    this.searchTerm = f.filters.searchTerm || '';
    this.loadTasks();
  }

  deleteFilter(index: number): void {
    this.savedFilters.splice(index, 1);
    localStorage.setItem('taskmanager_saved_filters', JSON.stringify(this.savedFilters));
  }

  openTokens(): void {
    this.showTokensPanel = true;
    this.newTokenResult = '';
    this.taskService.getTokens().subscribe({
      next: (data) => { this.tokens = data; },
    });
  }

  createApiToken(): void {
    if (!this.newTokenName.trim()) return;
    this.taskService.createToken(this.newTokenName.trim()).subscribe({
      next: (data) => {
        this.newTokenResult = data.token;
        this.newTokenName = '';
        this.tokens.unshift(data);
        this.toast.show('Token creado', 'success');
      },
      error: () => this.toast.show('Error al crear token', 'error'),
    });
  }

  deleteApiToken(tokenId: number): void {
    this.taskService.deleteToken(tokenId).subscribe({
      next: () => {
        this.tokens = this.tokens.filter((t: any) => t.id !== tokenId);
        this.toast.show('Token eliminado', 'info');
      },
    });
  }

  setReminder(task: Task, minutes: number): void {
    const reminders = JSON.parse(localStorage.getItem('taskmanager_reminders') || '{}');
    reminders[task.id] = { minutes, until: new Date(task.fecha_vencimiento!).getTime() - minutes * 60000, taskTitle: task.titulo };
    localStorage.setItem('taskmanager_reminders', JSON.stringify(reminders));
    this.reminderMinutes = minutes;
    this.toast.show(`Recordatorio: ${minutes} min antes`, 'info');
  }

  checkReminders(): void {
    const reminders = JSON.parse(localStorage.getItem('taskmanager_reminders') || '{}');
    const now = Date.now();
    let changed = false;
    for (const key of Object.keys(reminders)) {
      const r = reminders[key];
      if (r.until <= now) {
        this.toast.show(`⏰ Recordatorio: "${r.taskTitle}"`, 'info');
        delete reminders[key];
        changed = true;
      }
    }
    if (changed) localStorage.setItem('taskmanager_reminders', JSON.stringify(reminders));
  }
}
