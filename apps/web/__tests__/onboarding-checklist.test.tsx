import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnboardingChecklist } from "@/components/onboarding-checklist";

describe("OnboardingChecklist", () => {
  it("shows steps", () => {
    const { container } = render(<OnboardingChecklist steps={["Step 1", "Step 2"]} completed={["Step 1"]} />);
    expect(container.textContent).toContain("Step 1");
    expect(container.textContent).toContain("Step 2");
    expect(container.textContent).toContain("50%");
  });
  it("marks completed", () => {
    const { container } = render(<OnboardingChecklist steps={["A", "B"]} completed={["A"]} />);
    expect(container.textContent).toContain("✅");
    expect(container.textContent).toContain("⬜");
  });
});
