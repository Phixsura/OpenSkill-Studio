import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkflowBuilderCanvas } from "@/components/workflow-builder-canvas";

describe("WorkflowBuilderCanvas", () => {
  it("renders steps", () => {
    const steps = [{ type: "trigger" as const, config: {} }, { type: "action" as const, config: {} }];
    const { container } = render(<WorkflowBuilderCanvas steps={steps} onAddAction={vi.fn()} onRemoveStep={vi.fn()} />);
    expect(container.textContent).toContain("Trigger");
    expect(container.textContent).toContain("Action 1");
  });
  it("add action", () => {
    const fn = vi.fn();
    const { container } = render(<WorkflowBuilderCanvas steps={[]} onAddAction={fn} onRemoveStep={vi.fn()} />);
    fireEvent.click(container.querySelector("button")!);
    expect(fn).toHaveBeenCalled();
  });
});
