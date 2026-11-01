import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { OnboardingCompletePage } from "@/components/onboarding-complete-page";

describe("OnboardingCompletePage", () => {
  const steps = [{ label: "Create App", href: "/apps/new", icon: "📦", primary: true }];
  it("renders complete page", () => {
    const { container } = render(
      <OnboardingCompletePage headline="Welcome, Alice!" subtitle="Ready to go"
        planLabel="Pro" nextSteps={steps} onNavigate={vi.fn()} />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("Ready to go");
    expect(container.textContent).toContain("Pro Plan");
    expect(container.textContent).toContain("Create App");
  });
});
