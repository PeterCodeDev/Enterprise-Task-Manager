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
  user_id: number;
  categories: Category[];
}

export interface TaskCreate {
  titulo: string;
  descripcion: string | null;
  category_ids: number[];
}
