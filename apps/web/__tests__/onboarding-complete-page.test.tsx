import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnboardingCompletePage } from "@/components/onboarding-complete-page";

describe("OnboardingCompletePage", () => {
  it("renders", () => {
    const nextSteps = [{ label: "Dashboard", url: "/dev", icon: "📊" }];
    const { container } = render(
      <OnboardingCompletePage message="Welcome, Alice!"
        achievements={["Created account", "Published app"]} nextSteps={nextSteps} />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("Created account");
    expect(container.textContent).toContain("Published app");
    expect(container.textContent).toContain("Dashboard");
    expect(container.textContent).toContain("🎉");
  });
});
