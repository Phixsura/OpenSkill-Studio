import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RunbookExecutorView } from "@/components/runbook-executor-view";

describe("RunbookExecutorView", () => {
  it("renders runbook", () => {
    const { container } = render(
      <RunbookExecutorView name="Deploy" status="in_progress" progressPct={33}
        onExecuteStep={vi.fn()} steps={[
          { index: 0, title: "Backup DB", description: "", type: "automated", status: "success" },
          { index: 1, title: "Run Migrations", description: "", type: "automated", status: "pending" },
          { index: 2, title: "Verify", description: "", type: "manual", status: "pending" },
        ]} />
    );
    expect(container.textContent).toContain("Deploy");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("Backup DB");
    expect(container.textContent).toContain("Run Migrations");
    expect(container.textContent).toContain("Run");
  });
});
