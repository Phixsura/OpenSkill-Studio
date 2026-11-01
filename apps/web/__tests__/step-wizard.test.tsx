import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { StepWizard } from "@/components/step-wizard";

describe("StepWizard", () => {
  const steps = [
    { index: 0, title: "Account", description: "", icon: "1", status: "completed", optional: false },
    { index: 1, title: "Configure", description: "", icon: "2", status: "current", optional: false },
    { index: 2, title: "Review", description: "", icon: "3", status: "upcoming", optional: false },
  ];
  it("renders steps and progress", () => {
    const { container } = render(
      <StepWizard steps={steps} progressPct={33} onBack={vi.fn()} onNext={vi.fn()} canGoBack canGoNext isFinal={false} />
    );
    expect(container.textContent).toContain("Account");
    expect(container.textContent).toContain("Configure");
    expect(container.textContent).toContain("Next");
  });
  it("calls onNext", () => {
    const fn = vi.fn();
    const { container } = render(
      <StepWizard steps={steps} progressPct={33} onBack={vi.fn()} onNext={fn} canGoBack canGoNext isFinal={false} />
    );
    const next = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Next")!;
    fireEvent.click(next);
    expect(fn).toHaveBeenCalled();
  });
});
