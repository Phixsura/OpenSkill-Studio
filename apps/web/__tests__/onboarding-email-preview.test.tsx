import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnboardingEmailPreview } from "@/components/onboarding-email-preview";

describe("OnboardingEmailPreview", () => {
  const steps = [
    { step: 1, title: "Complete profile", url: "/settings" },
    { step: 2, title: "Create app", url: "/apps/new" },
  ];
  it("renders", () => {
    const { container } = render(
      <OnboardingEmailPreview subject="Welcome, Alice!" developerName="Alice" plan="pro"
        steps={steps} ctaLabel="Get Started" ctaUrl="/start" />
    );
    expect(container.textContent).toContain("Welcome, Alice!");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("Complete profile");
    expect(container.textContent).toContain("Create app");
    expect(container.textContent).toContain("Get Started");
  });
});
