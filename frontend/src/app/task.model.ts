export interface Task {
  id: number;
  titulo: string;
  descripcion: string | null;
  completada: boolean;
}

export interface TaskCreate {
  titulo: string;
  descripcion: string | null;
}
