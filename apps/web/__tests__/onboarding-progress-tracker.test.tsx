import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnboardingProgressTracker } from "@/components/onboarding-progress-tracker";

describe("OnboardingProgressTracker", () => {
  it("renders progress", () => {
    const steps = [
      { id: "account", title: "Create Account", points: 10, completed: true },
      { id: "profile", title: "Complete Profile", points: 15, completed: false },
    ];
    const { container } = render(
      <OnboardingProgressTracker steps={steps} progressPct={40} pointsEarned={10} pointsTotal={25}
        nextStep={steps[1]} />
    );
    expect(container.textContent).toContain("40%");
    expect(container.textContent).toContain("10/25 pts");
    expect(container.textContent).toContain("Next: Complete Profile");
  });
});
