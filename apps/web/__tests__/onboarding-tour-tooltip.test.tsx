import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingTourTooltip } from "@/components/onboarding-tour-tooltip";

describe("OnboardingTourTooltip", () => {
  const step = { step: 2, id: "search", title: "Find Apps", description: "Search apps",
    target: "#search", position: "bottom", completed: false };
  it("renders", () => {
    const { container } = render(
      <OnboardingTourTooltip currentStep={step} totalSteps={6} completedCount={1}
        onNext={vi.fn()} onSkip={vi.fn()} />
    );
    expect(container.textContent).toContain("Step 2 of 6");
    expect(container.textContent).toContain("Find Apps");
    expect(container.textContent).toContain("Next");
  });
  it("next", () => {
    const fn = vi.fn();
    const { container } = render(
      <OnboardingTourTooltip currentStep={step} totalSteps={6} completedCount={1}
        onNext={fn} onSkip={vi.fn()} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Next")!);
    expect(fn).toHaveBeenCalled();
  });
  it("hidden when null", () => {
    const { container } = render(
      <OnboardingTourTooltip currentStep={null} totalSteps={6} completedCount={6}
        onNext={vi.fn()} onSkip={vi.fn()} />
    );
    expect(container.innerHTML).toBe("");
  });
});
