import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingStepper } from "@/components/onboarding-stepper";

describe("OnboardingStepper", () => {
  it("renders stepper", () => {
    const { container } = render(
      <OnboardingStepper progressPct={33} onComplete={vi.fn()} onSkip={vi.fn()}
        steps={[
          { index: 0, title: "Create Account", description: "", required: true, completed: true },
          { index: 1, title: "Set Up Profile", description: "Add your info", required: true, completed: false },
          { index: 2, title: "Invite Team", description: "", required: false, completed: false },
        ]} />
    );
    expect(container.textContent).toContain("Getting Started");
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("Set Up Profile");
    expect(container.textContent).toContain("Done");
    expect(container.textContent).toContain("Skip");
  });
});
