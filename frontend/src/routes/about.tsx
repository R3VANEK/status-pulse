import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/about")({
  component: AboutComponent,
});

function AboutComponent() {
  return (
    <div className="p-2">
      <h3>About1</h3>

      <h1 className="text-blue text-3xl font-bold">Hello world!</h1>
    </div>
  );
}
