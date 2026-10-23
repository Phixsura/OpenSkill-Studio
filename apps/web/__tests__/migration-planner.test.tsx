import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MigrationPlanner } from "@/components/migration-planner";

describe("MigrationPlanner", () => {
  const steps = [
    { order: 1, name: "Add column", description: "Add status column", type: "schema", risk: "low", reversible: true, estimated_seconds: 5 },
    { order: 2, name: "Drop old", description: "", type: "schema", risk: "high", reversible: false, estimated_seconds: 2 },
  ];
  it("renders migration steps", () => {
    const { container } = render(
      <MigrationPlanner steps={steps} totalEstimatedSeconds={7} hasIrreversible={true} />
    );
    expect(container.textContent).toContain("Add column");
    expect(container.textContent).toContain("Drop old");
    expect(container.textContent).toContain("irreversible");
    expect(container.textContent).toContain("2 steps");
    expect(container.textContent).toContain("~7s");
  });
});
