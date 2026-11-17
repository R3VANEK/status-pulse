import { MOCK_PROJECTS, MOCK_PROJECTS_TOTAL } from "../../mocks/projects";
import { Button } from "../atoms/Button";
import { SearchInput } from "../atoms/SearchInput";
import { ProjectCard } from "../molecules/ProjectCard";
import { ProjectsTable } from "../organisms/ProjectsTable";

export function ProjectsPage() {
  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-6 px-4 py-6 md:px-8 md:py-8">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-fg text-2xl font-semibold md:text-3xl">
            Projekty
          </h1>
          <p className="text-fg-muted mt-1 text-sm">
            <span className="md:hidden">Zarządzaj pracą zespołu</span>
            <span className="hidden md:inline">
              Zarządzaj projektami i pracą swojego zespołu
            </span>
          </p>
        </div>
        <Button className="w-full md:w-auto">+ Nowy projekt</Button>
      </header>

      <div className="hidden md:block">
        <ProjectsTable projects={MOCK_PROJECTS} total={MOCK_PROJECTS_TOTAL} />
      </div>

      <div className="flex flex-col gap-4 md:hidden">
        <SearchInput
          placeholder="Szukaj projektu…"
          aria-label="Szukaj projektu"
        />
        <ul className="flex flex-col gap-3">
          {MOCK_PROJECTS.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </ul>
      </div>
    </main>
  );
}
