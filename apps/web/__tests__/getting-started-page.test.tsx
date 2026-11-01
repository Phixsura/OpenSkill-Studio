import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { GettingStartedPage } from "@/components/getting-started-page";

describe("GettingStartedPage", () => {
  const steps = [
    { id: "signup", title: "Create Account", icon: "👤", time_min: 2, completed: true },
    { id: "verify", title: "Verify Email", icon: "📧", time_min: 1, completed: false },
  ];
  it("renders", () => {
    const { container } = render(
      <GettingStartedPage developerName="Alice" steps={steps} completed={1} total={2}
        pct={50} currentStep={steps[1]} remainingTimeMin={1} allDone={false}
        onStepClick={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("1/2 completed");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Create Account");
    expect(container.textContent).toContain("✓");
    expect(container.textContent).toContain("Verify Email");
    expect(container.textContent).toContain("1 min remaining");
  });
});
