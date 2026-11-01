import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkflowTriggerPanel } from "@/components/workflow-trigger-panel";

const mockTriggers = [
  { id: "t1", name: "On Push", type: "webhook" as const, status: "active" as const,
    conditions: [{ field: "branch", operator: "eq", value: "main" }],
    fireCount: 42, lastFired: "2 min ago" },
  { id: "t2", name: "Nightly Build", type: "cron" as const, status: "paused" as const,
    conditions: [], cronExpression: "0 2 * * *", fireCount: 100 },
  { id: "t3", name: "Deploy", type: "manual" as const, status: "active" as const,
    conditions: [], fireCount: 5 },
];

describe("WorkflowTriggerPanel", () => {
  it("renders triggers with status", () => {
    const { container } = render(
      <WorkflowTriggerPanel triggers={mockTriggers} workflowName="CI Pipeline" />
    );
    expect(container.textContent).toContain("CI Pipeline");
    expect(container.textContent).toContain("On Push");
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("42");
  });

  it("shows fire button for manual triggers", () => {
    const onFire = vi.fn();
    const { getByText } = render(
      <WorkflowTriggerPanel triggers={mockTriggers} workflowName="Test" onFire={onFire} />
    );
    fireEvent.click(getByText("Fire"));
    expect(onFire).toHaveBeenCalledWith("t3");
  });

  it("expands to show conditions", () => {
    const { container } = render(
      <WorkflowTriggerPanel triggers={mockTriggers} workflowName="Test" />
    );
    const pushRow = container.querySelector('[class*="cursor-pointer"]');
    if (pushRow) fireEvent.click(pushRow);
    expect(container.textContent).toContain("branch");
    expect(container.textContent).toContain("eq");
  });

  it("shows empty state", () => {
    const { container } = render(
      <WorkflowTriggerPanel triggers={[]} workflowName="Empty" />
    );
    expect(container.textContent).toContain("No triggers configured");
  });
});
