import { useQuery } from "@tanstack/react-query";
import { programsQueryOptions } from "../api/programs";

export function ProgramsList() {
  const {
    data: programs,
    isPending,
    isSuccess,
    isError,
    error,
    isFetching,
    refetch,
  } = useQuery(programsQueryOptions());

  return (
    <div className="mt-4">
      <h2 className="text-xl font-semibold">Programs</h2>

      {isPending && <p className="mt-2">Loading programs...</p>}

      {isError && (
        <div className="mt-2">
          <p className="text-red-500">
            {error instanceof Error ? error.message : "Something went wrong"}
          </p>
          <button
            type="button"
            className="mt-2 rounded border border-red-500 px-2 py-1 text-red-500"
            onClick={() => void refetch()}
          >
            Retry
          </button>
        </div>
      )}

      {isSuccess && programs?.length === 0 && (
        <p className="mt-2">No programs found.</p>
      )}

      {isSuccess && programs && programs.length > 0 && (
        <ul className="mt-2 list-disc pl-6 text-left">
          {programs.map((program) => (
            <li key={program.id}>{program.text}</li>
          ))}
        </ul>
      )}

      {isFetching && !isPending && (
        <p className="mt-2 text-sm opacity-60">Refreshing...</p>
      )}
    </div>
  );
}
