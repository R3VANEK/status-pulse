import { PROJECT_STATUS_LABELS, type ProjectStatus } from "../../types/project";

const STATUS_CLASSES: Record<ProjectStatus, string> = {
  planned: "bg-primary-soft text-on-primary-soft",
  in_progress: "bg-primary-soft text-on-primary-soft",
  completed: "bg-success-soft text-on-success-soft",
};

type StatusBadgeProps = {
  status: ProjectStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span
      className={`inline-flex h-7 items-center rounded-full px-3 text-xs font-semibold ${STATUS_CLASSES[status]}`}
    >
      {PROJECT_STATUS_LABELS[status]}
    </span>
  );
}
