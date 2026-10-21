import { createFileRoute } from "@tanstack/react-router";
import { ProgramsList } from "../components/ProgramsList";

export const Route = createFileRoute("/about")({
  component: AboutComponent,
});

function AboutComponent() {
  return (
    <div className="p-2">
      <h3>About1</h3>

      <h1 className="text-blue text-3xl font-bold">Hello world!</h1>

      <ProgramsList />
    </div>
  );
}
