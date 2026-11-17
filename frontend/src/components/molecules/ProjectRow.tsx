import type { Project } from "../../types/project";
import { ProjectIcon } from "../atoms/ProjectIcon";
import { StatusBadge } from "../atoms/StatusBadge";
import { ActionsMenu } from "./ActionsMenu";

type ProjectRowProps = {
  project: Project;
};

export function ProjectRow({ project }: ProjectRowProps) {
  return (
    <tr className="border-line border-t">
      <td className="px-6 py-4">
        <div className="flex items-center gap-3">
          <ProjectIcon />
          <div>
            <p className="text-fg font-medium">{project.name}</p>
            <p className="text-fg-muted text-sm">
              {project.category} • {project.code}
            </p>
          </div>
        </div>
      </td>
      <td className="px-6 py-4">
        <StatusBadge status={project.status} />
      </td>
      <td className="px-6 py-4">
        <div className="flex -space-x-2">
          {project.team.map((initials) => (
            <span
              key={initials}
              className="border-surface bg-primary-soft text-on-primary-soft flex size-8 items-center justify-center rounded-full border-2 text-xs font-medium"
            >
              {initials}
            </span>
          ))}
        </div>
      </td>
      <td className="text-fg px-6 py-4 text-sm">
        {project.tasksDone} / {project.tasksTotal}
      </td>
      <td className="px-6 py-4 text-right">
        <ActionsMenu />
      </td>
    </tr>
  );
}
