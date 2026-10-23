import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkflowListPanel } from "@/components/workflow-list-panel";

describe("WorkflowListPanel", () => {
  it("renders workflows", () => {
    const onRun = vi.fn();
    const { container, getByText } = render(
      <WorkflowListPanel onToggle={vi.fn()} onRun={onRun}
        workflows={[
          { id: "wf1", name: "Deploy Pipeline", trigger: "push_to_main", enabled: true, steps: 3, runs: 5, lastStatus: "success" },
        ]} />
    );
    expect(container.textContent).toContain("Workflows");
    expect(container.textContent).toContain("Deploy Pipeline");
    expect(container.textContent).toContain("3 steps");
    expect(container.textContent).toContain("5 runs");
    expect(container.textContent).toContain("success");
    fireEvent.click(getByText("Run"));
    expect(onRun).toHaveBeenCalledWith("wf1");
  });
});
