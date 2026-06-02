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
  recurrencia: string | null;
  fecha_vencimiento: string | null;
  user_id: number;
  categories: Category[];
  subtasks: Subtask[];
  attachments: Attachment[];
  comments: Comment[];
}

export interface Comment {
  id: number;
  task_id: number;
  texto: string;
  created_at: string;
}

export interface Subtask {
  id: number;
  task_id: number;
  texto: string;
  completada: boolean;
}

export interface Attachment {
  id: number;
  task_id: number;
  original_name: string;
  size: number;
  created_at: string;
}

export interface TaskCreate {
  titulo: string;
  descripcion: string | null;
  category_ids: number[];
  prioridad: string;
  estado: string;
  recurrencia: string | null;
  fecha_vencimiento: string | null;
}
