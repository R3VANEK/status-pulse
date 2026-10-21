import { queryOptions } from "@tanstack/react-query";

export type Program = {
  id: string;
  text: string;
};

const API_BASE_URL: string =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api";

export class ApiError extends Error {
  readonly status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export async function fetchPrograms(signal?: AbortSignal): Promise<Program[]> {
  const response = await fetch(`${API_BASE_URL}/programs`, { signal });

  if (!response.ok) {
    throw new ApiError(
      `Failed to fetch programs (${response.status} ${response.statusText})`,
      response.status,
    );
  }

  const data: unknown = await response.json();

  if (!Array.isArray(data)) {
    throw new ApiError(
      "Unexpected response: expected a list of programs",
      response.status,
    );
  }

  return data as Program[];
}

export function programsQueryOptions() {
  return queryOptions({
    queryKey: ["programs"] as const,
    queryFn: ({ signal }) => fetchPrograms(signal),
  });
}
