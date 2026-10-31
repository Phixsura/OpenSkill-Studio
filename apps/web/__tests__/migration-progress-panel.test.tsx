import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { MigrationProgressPanel } from "@/components/migration-progress-panel";

const progress = {
  status: "failed", total: 3, completed: 1, percentage: 33,
  steps: [
    { stepId: "s-1", name: "Schema", description: "Update schema", status: "completed", error: "" },
    { stepId: "s-2", name: "Data", description: "Migrate data", status: "failed", error: "DB timeout" },
    { stepId: "s-3", name: "Index", description: "Rebuild indexes", status: "pending", error: "" },
  ],
};

describe("MigrationProgressPanel", () => {
  it("renders progress", () => {
    const { container } = render(<MigrationProgressPanel progress={progress} />);
    expect(container.textContent).toContain("1/3 steps (33%)");
    expect(container.textContent).toContain("DB timeout");
    expect(container.textContent).toContain("Rollback");
  });
  it("rollback", () => {
    const fn = vi.fn();
    const { container } = render(<MigrationProgressPanel progress={progress} onRollback={fn} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
