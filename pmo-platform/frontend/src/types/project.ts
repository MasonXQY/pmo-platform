export interface Project {
  id: string;
  name: string;
  description?: string;
  status: string;
  budget?: number;
  health_score: number;
}
