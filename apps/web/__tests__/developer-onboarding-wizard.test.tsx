import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DeveloperOnboardingWizard } from "@/components/developer-onboarding-wizard";

const mockSteps = [
  { id: "profile", title: "Set up profile", description: "Add your name and avatar", icon: "1", completed: true },
  { id: "api-key", title: "Create API key", description: "Generate your first API key", icon: "2", completed: false, action: "Generate API Key" },
  { id: "template", title: "Choose template", description: "Pick a starter template", icon: "3", completed: false },
  { id: "publish", title: "Publish extension", description: "Submit to marketplace", icon: "4", completed: false },
];

describe("DeveloperOnboardingWizard", () => {
  it("renders welcome and progress", () => {
    const { container } = render(
      <DeveloperOnboardingWizard steps={mockSteps} developerName="Alice" />
    );
    expect(container.textContent).toContain("Welcome, Alice");
    expect(container.textContent).toContain("1 of 4 complete");
    expect(container.textContent).toContain("25%");
  });

  it("shows completed step with checkmark", () => {
    const { container } = render(
      <DeveloperOnboardingWizard steps={mockSteps} developerName="Alice" />
    );
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("Set up profile");
  });

  it("shows action button for current step", () => {
    const onAction = vi.fn();
    const { getByText } = render(
      <DeveloperOnboardingWizard steps={mockSteps} developerName="Alice" onStepAction={onAction} />
    );
    fireEvent.click(getByText("Generate API Key"));
    expect(onAction).toHaveBeenCalledWith("api-key");
  });

  it("shows completion when all done", () => {
    const allDone = mockSteps.map((s) => ({ ...s, completed: true }));
    const { container } = render(
      <DeveloperOnboardingWizard steps={allDone} developerName="Alice" />
    );
    expect(container.textContent).toContain("All set!");
    expect(container.textContent).toContain("Start Building");
  });
});
