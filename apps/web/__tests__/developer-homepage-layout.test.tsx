import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { DeveloperHomepageLayout } from "@/components/developer-homepage-layout";

describe("DeveloperHomepageLayout", () => {
  it("renders homepage", () => {
    const stats = [{ key: "apps", label: "Apps", value: 5, icon: "📦" }];
    const actions = [{ label: "Create", url: "/new", icon: "➕", primary: true }];
    const { container } = render(
      <DeveloperHomepageLayout name="DevCo" plan="pro" verified={true}
        statsCards={stats} quickActions={actions} hasOnboarding={false} />
    );
    expect(container.textContent).toContain("Welcome back, DevCo!");
    expect(container.textContent).toContain("pro");
    expect(container.textContent).toContain("5");
  });
  it("shows onboarding", () => {
    const { container } = render(
      <DeveloperHomepageLayout name="New" plan="free" verified={false}
        statsCards={[]} quickActions={[]} hasOnboarding={true} onboardingPct={25} />
    );
    expect(container.textContent).toContain("25% complete");
  });
});
