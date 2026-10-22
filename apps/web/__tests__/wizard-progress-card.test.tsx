import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WizardProgressCard } from "@/components/wizard-progress-card";

const STEPS = [{ id: "a", title: "Step A", description: "" }, { id: "b", title: "Step B", description: "" }];

describe("WizardProgressCard", () => {
  it("shows progress", () => {
    const { container } = render(<WizardProgressCard steps={STEPS} completedSteps={["a"]} pct={50} currentStep={STEPS[1]} />);
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Step B");
  });
  it("marks completed", () => {
    const { container } = render(<WizardProgressCard steps={STEPS} completedSteps={["a"]} pct={50} currentStep={null} />);
    expect(container.textContent).toContain("✅");
  });
});
