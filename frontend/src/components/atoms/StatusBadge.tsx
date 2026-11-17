import type { ProjectStatus } from "../../types/project";

const STATUS_STYLES: Record<
  ProjectStatus,
  { label: string; className: string }
> = {
  planned: {
    label: "Planowany",
    className: "bg-primary-soft text-on-primary-soft",
  },
  in_progress: {
    label: "W trakcie",
    className: "bg-primary-soft text-on-primary-soft",
  },
  completed: {
    label: "Zakończony",
    className: "bg-success-soft text-on-success-soft",
  },
};

type StatusBadgeProps = {
  status: ProjectStatus;
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const { label, className } = STATUS_STYLES[status];

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${className}`}
    >
      {label}
    </span>
  );
}
