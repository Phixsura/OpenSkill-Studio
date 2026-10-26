import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingWizardPanel } from "@/components/onboarding-wizard-panel";

const mockSteps = [
  { stepId: "basics", title: "Extension Basics", description: "Name and desc", required: true, completed: true, skipped: false },
  { stepId: "manifest", title: "Create Manifest", description: "Config", required: true, completed: false, skipped: false },
  { stepId: "branding", title: "Add Branding", description: "Icon", required: false, completed: false, skipped: false },
];
const mockProgress = { currentStep: 1, totalSteps: 3, percent: 33, isComplete: false };

describe("OnboardingWizardPanel", () => {
  it("renders current step", () => {
    const { container } = render(<OnboardingWizardPanel steps={mockSteps} progress={mockProgress} />);
    expect(container.textContent).toContain("Create Manifest");
    expect(container.textContent).toContain("Step 2/3");
  });

  it("calls onComplete", () => {
    const onComplete = vi.fn();
    const { getByText } = render(<OnboardingWizardPanel steps={mockSteps} progress={mockProgress} onComplete={onComplete} />);
    fireEvent.click(getByText("Continue"));
    expect(onComplete).toHaveBeenCalled();
  });

  it("shows completion screen", () => {
    const done = { ...mockProgress, isComplete: true };
    const { container } = render(<OnboardingWizardPanel steps={mockSteps} progress={done} />);
    expect(container.textContent).toContain("Setup Complete!");
  });
});
