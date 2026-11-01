import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeployHistoryTable } from "@/components/deploy-history-table";

describe("DeployHistoryTable", () => {
  const deploys = [
    { id: "d1", version: "2.0.0", environment: "prod", status: "success", deployedAt: "2026-03-01",
      deployer: "Alice", commit: "abc123", durationS: 120, isCurrent: true, canRollback: false },
    { id: "d2", version: "1.5.0", environment: "prod", status: "success", deployedAt: "2026-02-01",
      deployer: "Bob", commit: "def456", durationS: 90, isCurrent: false, canRollback: true },
  ];
  it("renders history", () => {
    const { container } = render(
      <DeployHistoryTable deploys={deploys} successRate={100} avgDurationS={105} onRollback={vi.fn()} />
    );
    expect(container.textContent).toContain("Deploy History");
    expect(container.textContent).toContain("v2.0.0");
    expect(container.textContent).toContain("Current");
    expect(container.textContent).toContain("Rollback");
    expect(container.textContent).toContain("100%");
  });
});
