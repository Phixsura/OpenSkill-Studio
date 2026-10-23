import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingWizardFlow } from "@/components/onboarding-wizard-flow";

describe("OnboardingWizardFlow", () => {
  const steps = [
    { id: "name", title: "Name", description: "Choose name", required: true, completed: true },
    { id: "desc", title: "Description", description: "Describe it", required: true, completed: false },
  ];
  it("renders", () => {
    const { container } = render(
      <OnboardingWizardFlow steps={steps} currentStep="desc" progressPct={50}
        canSubmit={false} onStepClick={vi.fn()} onSubmit={vi.fn()} />
    );
    expect(container.textContent).toContain("Create Your App");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("Description");
    expect(container.textContent).toContain("Complete required");
  });
  it("step click", () => {
    const fn = vi.fn();
    const { container } = render(
      <OnboardingWizardFlow steps={steps} currentStep="desc" progressPct={50}
        canSubmit={false} onStepClick={fn} onSubmit={vi.fn()} />
    );
    fireEvent.click(container.querySelectorAll("button")[0]);
    expect(fn).toHaveBeenCalledWith("name");
  });
});
