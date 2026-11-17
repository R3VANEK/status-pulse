import type { Project } from "../../types/project";
import { ProjectIcon } from "../atoms/ProjectIcon";
import { StatusBadge } from "../atoms/StatusBadge";
import { ActionsMenu } from "./ActionsMenu";

const CELL_CLASS = "border-y border-line px-4 py-4";

type ProjectRowProps = {
  project: Project;
};

export function ProjectRow({ project }: ProjectRowProps) {
  return (
    <tr>
      <td className={`${CELL_CLASS} rounded-l-control border-l pl-2`}>
        <div className="flex items-center gap-4">
          <ProjectIcon />
          <div>
            <p className="text-fg text-sm font-semibold">{project.name}</p>
            <p className="text-fg-muted mt-1 text-xs">
              {project.category} • {project.code}
            </p>
          </div>
        </div>
      </td>
      <td className={CELL_CLASS}>
        <StatusBadge status={project.status} />
      </td>
      <td className={`${CELL_CLASS} text-fg text-[13px] font-semibold`}>
        {project.team.join(" ")}
      </td>
      <td className={`${CELL_CLASS} text-fg text-[13px]`}>
        {project.tasksDone} / {project.tasksTotal}
      </td>
      <td
        className={`${CELL_CLASS} rounded-r-control border-r pr-2 text-right`}
      >
        <ActionsMenu />
      </td>
    </tr>
  );
}
