import { createFileRoute } from "@tanstack/react-router";
import { Button } from "../components/atoms/Button";
import { ProjectIcon } from "../components/atoms/ProjectIcon";
import { SearchInput } from "../components/atoms/SearchInput";
import { StatusBadge } from "../components/atoms/StatusBadge";

export const Route = createFileRoute("/projects")({
  component: ProjectsPage,
});

function ProjectsPage() {
  return (
    <div className="flex flex-col gap-4 p-6">
      <h1 className="text-2xl font-semibold">Projekty</h1>
      <Button>+ Nowy projekt</Button>
      <SearchInput
        placeholder="Szukaj projektu…"
        aria-label="Szukaj projektu"
      />
      <div className="flex gap-2">
        <StatusBadge status="planned" />
        <StatusBadge status="in_progress" />
        <StatusBadge status="completed" />
      </div>
      <ProjectIcon />
    </div>
  );
}
