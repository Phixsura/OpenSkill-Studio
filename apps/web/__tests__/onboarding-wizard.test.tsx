import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingWizard } from "@/components/onboarding-wizard";

describe("OnboardingWizard", () => {
  const steps = [
    { id: "profile", title: "Complete Profile", description: "Add info", icon: "👤", required: true, completed: true },
    { id: "cli", title: "Install CLI", description: "Get the CLI", icon: "💻", required: true, completed: false },
  ];
  it("renders onboarding", () => {
    const { container } = render(
      <OnboardingWizard steps={steps} progressPct={50} canSkip={false}
        nextStep={steps[1]} onComplete={vi.fn()} onSkip={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome to OpenSkill!");
    expect(container.textContent).toContain("Complete Profile");
    expect(container.textContent).toContain("Install CLI");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Start");
  });
});
