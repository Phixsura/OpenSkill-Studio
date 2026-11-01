import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingFlowWizard } from "@/components/onboarding-flow-wizard";

describe("OnboardingFlowWizard", () => {
  const steps = [
    { key: "welcome", title: "Welcome", type: "info", completed: true, current: false, required: true },
    { key: "profile", title: "Create Profile", type: "form", completed: false, current: true, required: true },
    { key: "app", title: "Create App", type: "wizard", completed: false, current: false, required: true },
  ];
  it("renders", () => {
    const { container } = render(
      <OnboardingFlowWizard steps={steps} progressPct={33} currentStep={steps[1]}
        tips={["Add a bio"]} onCompleteStep={vi.fn()} onSkip={vi.fn()} />
    );
    expect(container.textContent).toContain("Get Started");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("Create Profile");
    expect(container.textContent).toContain("Add a bio");
  });
  it("start button", () => {
    const fn = vi.fn();
    const { container } = render(
      <OnboardingFlowWizard steps={steps} progressPct={33} currentStep={steps[1]}
        tips={[]} onCompleteStep={fn} onSkip={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Start")!);
    expect(fn).toHaveBeenCalledWith("profile");
  });
});
