import { createFileRoute } from "@tanstack/react-router";
import { ProgramsList } from "../components/ProgramsList";

export const Route = createFileRoute("/")({
  component: IndexComponent,
});

function IndexComponent() {
  return (
    <div className="p-2">
      <h1 className="text-blue text-3xl font-bold">Status Pulse</h1>

      <ProgramsList />
    </div>
  );
}
