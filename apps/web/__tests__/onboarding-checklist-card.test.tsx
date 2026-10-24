import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingChecklistCard } from "@/components/onboarding-checklist-card";

describe("OnboardingChecklistCard", () => {
  const steps = [
    { id: "profile", label: "Complete profile", required: true, completed: true },
    { id: "app", label: "Create app", required: false, completed: false },
  ];
  it("renders", () => {
    const { container } = render(
      <OnboardingChecklistCard steps={steps} progressPct={50} onStepClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("50% complete");
    expect(container.textContent).toContain("Complete profile");
    expect(container.textContent).toContain("Create app");
  });
  it("click step", () => {
    const fn = vi.fn();
    const { container } = render(
      <OnboardingChecklistCard steps={steps} progressPct={50} onStepClick={fn} />
    );
    const btns = container.querySelectorAll("button");
    fireEvent.click(btns[1]);
    expect(fn).toHaveBeenCalledWith("app");
  });
});
