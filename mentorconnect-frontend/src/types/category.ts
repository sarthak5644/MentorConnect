export interface Category {
  id: number;
  name: string;
  description?: string | null;
  is_active: boolean;
  fields?: Field[];
}

export interface Field {
  id: number;
  category_id: number;
  name: string;
  is_active: boolean;
}