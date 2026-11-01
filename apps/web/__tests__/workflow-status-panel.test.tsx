import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkflowStatusPanel } from "@/components/workflow-status-panel";

const mockRuns = [
  {
    id: "r1", name: "Publish Pipeline", trigger: "push", status: "completed" as const,
    startedAt: "10:30", duration: "2m 15s",
    steps: [
      { name: "Install", status: "passed" as const },
      { name: "Lint", status: "passed" as const },
      { name: "Test", status: "passed" as const },
      { name: "Build", status: "passed" as const },
    ],
  },
  {
    id: "r2", name: "Security Scan", trigger: "schedule", status: "failed" as const,
    startedAt: "09:00", duration: "45s",
    steps: [
      { name: "Scan", status: "passed" as const },
      { name: "Audit", status: "failed" as const },
      { name: "Report", status: "skipped" as const },
    ],
  },
];

describe("WorkflowStatusPanel", () => {
  it("renders workflow runs", () => {
    const { container } = render(<WorkflowStatusPanel runs={mockRuns} />);
    expect(container.textContent).toContain("Workflow Runs");
    expect(container.textContent).toContain("Publish Pipeline");
    expect(container.textContent).toContain("Security Scan");
  });

  it("shows step names and status", () => {
    const { container } = render(<WorkflowStatusPanel runs={mockRuns} />);
    expect(container.textContent).toContain("Install");
    expect(container.textContent).toContain("Lint");
    expect(container.textContent).toContain("Audit");
  });

  it("shows retry for failed runs", () => {
    const onRetry = vi.fn();
    const { getByText } = render(<WorkflowStatusPanel runs={mockRuns} onRetry={onRetry} />);
    fireEvent.click(getByText("Retry"));
    expect(onRetry).toHaveBeenCalledWith("r2");
  });
});
