import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { WorkflowBuilderCanvas } from "@/components/workflow-builder-canvas";

describe("WorkflowBuilderCanvas", () => {
  const trigger = { type: "event", label: "Platform event" };
  const steps = [
    { step: 1, type: "send_email", label: "Send Email" },
    { step: 2, type: "notify", label: "Send Notification" },
  ];
  it("renders", () => {
    const { container } = render(
      <WorkflowBuilderCanvas name="On Install" trigger={trigger} steps={steps}
        status="draft" onAddStep={vi.fn()} onActivate={vi.fn()} />
    );
    expect(container.textContent).toContain("On Install");
    expect(container.textContent).toContain("Platform event");
    expect(container.textContent).toContain("📧");
    expect(container.textContent).toContain("Send Email");
    expect(container.textContent).toContain("Activate Workflow");
  });
  it("activate", () => {
    const fn = vi.fn();
    const { container } = render(
      <WorkflowBuilderCanvas name="X" trigger={trigger} steps={steps}
        status="draft" onAddStep={vi.fn()} onActivate={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Activate Workflow")!);
    expect(fn).toHaveBeenCalled();
  });
});
