export interface Category {
  id: number;
  nombre: string;
  color: string;
}

export interface Task {
  id: number;
  titulo: string;
  descripcion: string | null;
  completada: boolean;
  prioridad: string;
  estado: string;
  fecha_vencimiento: string | null;
  user_id: number;
  categories: Category[];
  subtasks: Subtask[];
}

export interface Subtask {
  id: number;
  task_id: number;
  texto: string;
  completada: boolean;
}

export interface TaskCreate {
  titulo: string;
  descripcion: string | null;
  category_ids: number[];
  prioridad: string;
  estado: string;
  fecha_vencimiento: string | null;
}
