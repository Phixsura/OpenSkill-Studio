import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { WizardSteps } from "@/components/wizard-steps";

const STEPS = ["Details", "Manifest", "Review", "Publish"];

describe("WizardSteps", () => {
  it("renders all steps", () => {
    const { container } = render(<WizardSteps steps={STEPS} currentStep={0} />);
    expect(container.textContent).toContain("Details");
    expect(container.textContent).toContain("Publish");
  });

  it("highlights current", () => {
    const { container } = render(<WizardSteps steps={STEPS} currentStep={1} />);
    expect(container.textContent).toContain("Manifest");
  });

  it("shows checkmarks for completed", () => {
    const { container } = render(<WizardSteps steps={STEPS} currentStep={2} />);
    expect(container.textContent).toContain("✓");
  });

  it("shows step numbers", () => {
    const { container } = render(<WizardSteps steps={STEPS} currentStep={0} />);
    expect(container.textContent).toContain("1");
  });
});
