import { createFileRoute } from "@tanstack/react-router";
import { ProjectsTable } from "../components/organisms/ProjectsTable";
import { MOCK_PROJECTS, MOCK_PROJECTS_TOTAL } from "../mocks/projects";

export const Route = createFileRoute("/projects")({
  component: ProjectsPage,
});

function ProjectsPage() {
  return (
    <div className="p-6">
      <ProjectsTable projects={MOCK_PROJECTS} total={MOCK_PROJECTS_TOTAL} />
    </div>
  );
}
