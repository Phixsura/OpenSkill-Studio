import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { OnboardingChecklist } from "@/components/onboarding-checklist";

describe("OnboardingChecklist", () => {
  const steps = [
    { key: "profile", title: "Complete profile", required: true, completed: true },
    { key: "app", title: "Create app", required: true, completed: false },
    { key: "docs", title: "Add docs", required: false, completed: false },
  ];
  it("renders progress", () => {
    const { container } = render(<OnboardingChecklist steps={steps} progressPct={33} canPublish={false} />);
    expect(container.textContent).toContain("33%");
    expect(container.textContent).toContain("Complete profile");
  });
  it("shows required badge", () => {
    const { container } = render(<OnboardingChecklist steps={steps} progressPct={33} canPublish={false} />);
    expect(container.textContent).toContain("Required");
  });
  it("shows publish ready", () => {
    const { container } = render(<OnboardingChecklist steps={steps} progressPct={100} canPublish={true} />);
    expect(container.textContent).toContain("publish apps");
  });
});
