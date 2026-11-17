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
    <section className="border-line bg-surface rounded-card border p-6">
      <h2 className="text-fg text-lg font-bold">Wszystkie projekty</h2>
      <p className="text-fg-muted mt-1 text-[13px]">{total} projektów</p>

      <div className="mt-7 flex items-center gap-4">
        <SearchInput
          placeholder="Szukaj projektu…"
          aria-label="Szukaj projektu"
          className="w-full max-w-112.5"
        />
        <select
          aria-label="Filtruj po statusie"
          className="border-line bg-surface text-fg rounded-control h-10.5 w-37.5 border px-4 text-xs"
        >
          <option value="">Status: Wszystkie</option>
          {Object.entries(PROJECT_STATUS_LABELS).map(([value, label]) => (
            <option key={value} value={value}>
              {label}
            </option>
          ))}
        </select>
      </div>

      <div className="border-line mt-6 border-t" />

      <table className="mt-2 w-full border-separate border-spacing-y-2.5">
        <thead>
          <tr>
            {COLUMNS.map((column, index) => (
              <th
                key={column}
                scope="col"
                className={`text-fg-muted px-4 py-2 text-left text-[11px] font-semibold tracking-wide uppercase ${index === 0 ? "pl-2" : ""}`}
              >
                {column}
              </th>
            ))}
            <th scope="col" className="w-12">
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

      <div className="mt-4 flex items-center justify-between">
        <p className="text-fg-muted text-xs">
          Wyświetlono 1–{projects.length} z {total}
        </p>
        <Pagination currentPage={1} totalPages={totalPages} />
      </div>
    </section>
  );
}
