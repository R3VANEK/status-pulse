export type ProjectStatus = "planned" | "in_progress" | "completed";

export type Project = {
  id: string;
  code: string;
  name: string;
  category: string;
  status: ProjectStatus;
  team: string[];
  tasksDone: number;
  tasksTotal: number;
};

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  planned: "Planowany",
  in_progress: "W trakcie",
  completed: "Zakończony",
};
