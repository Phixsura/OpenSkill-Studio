import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MigrationStatusPanel } from "@/components/migration-status-panel";

describe("MigrationStatusPanel", () => {
  it("renders status", () => {
    const { container } = render(
      <MigrationStatusPanel applied={5} pending={2} latestApplied="005"
        upToDate={false} hasDestructive={true} estimatedDisplay="2m 30s"
        pendingMigrations={[{ id: "006" }, { id: "007", destructive: true }]}
        onRunMigrations={vi.fn()} />
    );
    expect(container.textContent).toContain("Migrations");
    expect(container.textContent).toContain("2 pending");
    expect(container.textContent).toContain("5");
    expect(container.textContent).toContain("005");
    expect(container.textContent).toContain("2m 30s");
    expect(container.textContent).toContain("destructive");
    expect(container.textContent).toContain("Run Migrations");
  });
});
