import type { Project } from "../../types/project";
import { StatusBadge } from "../atoms/StatusBadge";

type ProjectCardProps = {
  project: Project;
};

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <li className="border-line bg-surface rounded-xl border p-4">
      <p className="text-fg font-medium">{project.name}</p>
      <div className="mt-3 flex items-center justify-between gap-2">
        <p className="text-fg-muted text-sm">
          {project.code} • {project.tasksDone} / {project.tasksTotal} zadań
        </p>
        <StatusBadge status={project.status} />
      </div>
    </li>
  );
}
