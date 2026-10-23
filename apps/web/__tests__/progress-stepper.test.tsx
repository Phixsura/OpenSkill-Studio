import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ProgressStepper } from "@/components/progress-stepper";

describe("ProgressStepper", () => {
  const steps = [
    { index: 0, name: "Setup", status: "completed", description: "Done" },
    { index: 1, name: "Configure", status: "in_progress", description: "In progress" },
    { index: 2, name: "Deploy", status: "pending", description: "" },
  ];
  it("renders", () => {
    const { container } = render(
      <ProgressStepper title="App Setup" steps={steps} progressPct={33} currentStep={1} />
    );
    expect(container.textContent).toContain("App Setup");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("🔵");
    expect(container.textContent).toContain("⬜");
    expect(container.textContent).toContain("Setup");
    expect(container.textContent).toContain("Configure");
  });
});
