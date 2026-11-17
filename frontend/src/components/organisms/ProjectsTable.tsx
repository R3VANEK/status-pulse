import { PROJECT_STATUS_LABELS, type Project } from "../../types/project";
import { SearchInput } from "../atoms/SearchInput";
import { Pagination } from "../molecules/Pagination";
import { ProjectRow } from "../molecules/ProjectRow";

const PAGE_SIZE = 4;

const COLUMNS = ["Projekt", "Status", "Zespół", "Zadania"];

type ProjectsTableProps = {
  projects: Project[];
  total: number;
};

export function ProjectsTable({ projects, total }: ProjectsTableProps) {
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <section className="border-line bg-surface rounded-2xl border">
      <div className="flex items-center justify-between gap-4 px-6 py-5">
        <div>
          <h2 className="text-fg text-lg font-semibold">Wszystkie projekty</h2>
          <p className="text-fg-muted text-sm">{total} projektów</p>
        </div>
        <div className="flex items-center gap-3">
          <SearchInput
            placeholder="Szukaj projektu…"
            aria-label="Szukaj projektu"
            className="w-64"
          />
          <select
            aria-label="Filtruj po statusie"
            className="border-line bg-surface text-fg rounded-lg border px-3 py-2 text-sm"
          >
            <option value="">Status: Wszystkie</option>
            {Object.entries(PROJECT_STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>
      </div>

      <table className="w-full">
        <thead>
          <tr>
            {COLUMNS.map((column) => (
              <th
                key={column}
                scope="col"
                className="text-fg-muted px-6 py-3 text-left text-xs font-medium tracking-wide uppercase"
              >
                {column}
              </th>
            ))}
            <th scope="col">
              <span className="sr-only">Akcje</span>
            </th>
          </tr>
        </thead>
        <tbody>
          {projects.map((project) => (
            <ProjectRow key={project.id} project={project} />
          ))}
        </tbody>
      </table>

      <div className="border-line flex items-center justify-between border-t px-6 py-4">
        <p className="text-fg-muted text-sm">
          Wyświetlono 1–{projects.length} z {total}
        </p>
        <Pagination currentPage={1} totalPages={totalPages} />
      </div>
    </section>
  );
}
