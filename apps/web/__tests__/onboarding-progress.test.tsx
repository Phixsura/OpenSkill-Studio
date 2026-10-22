import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnboardingProgress } from "@/components/onboarding-progress";

const STEPS = [
  { key: "a", label: "Step A", required: true, completed: true },
  { key: "b", label: "Step B", required: true, completed: false },
  { key: "c", label: "Step C", required: false, completed: false },
];

describe("OnboardingProgress", () => {
  it("shows progress pct", () => {
    const { container } = render(<OnboardingProgress steps={STEPS} progressPct={33} requiredComplete={false} nextStep={{ key: "b", label: "Step B" }} />);
    expect(container.textContent).toContain("33%");
  });

  it("shows next step", () => {
    const { container } = render(<OnboardingProgress steps={STEPS} progressPct={33} requiredComplete={false} nextStep={{ key: "b", label: "Step B" }} />);
    expect(container.textContent).toContain("Step B");
  });

  it("shows completion message", () => {
    const { container } = render(<OnboardingProgress steps={STEPS} progressPct={100} requiredComplete={true} nextStep={null} />);
    expect(container.textContent).toContain("All required steps complete");
  });

  it("shows step list", () => {
    const { container } = render(<OnboardingProgress steps={STEPS} progressPct={33} requiredComplete={false} nextStep={null} />);
    expect(container.textContent).toContain("Step A");
    expect(container.textContent).toContain("Step C");
  });

  it("marks completed steps", () => {
    const { container } = render(<OnboardingProgress steps={STEPS} progressPct={33} requiredComplete={false} nextStep={null} />);
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⬜");
  });
});
