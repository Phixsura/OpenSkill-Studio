import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import PlanManagerCard from "../src/components/plan-manager-card";

const plans = [
  { plan_id: "free", name: "Free", features: ["basic_api"], price_cents: 0, isCurrent: false },
  {
    plan_id: "pro",
    name: "Pro",
    features: ["basic_api", "webhooks", "analytics"],
    price_cents: 2900,
    isCurrent: true,
  },
  {
    plan_id: "enterprise",
    name: "Enterprise",
    features: ["basic_api", "webhooks", "analytics", "sso"],
    price_cents: 9900,
    isCurrent: false,
  },
];

describe("PlanManagerCard", () => {
  it("renders header and app name", () => {
    const { container } = render(<PlanManagerCard plans={plans} appName="My App" />);
    expect(container.textContent).toContain("Plans");
    expect(container.textContent).toContain("My App");
  });

  it("shows current plan badge", () => {
    const { container } = render(<PlanManagerCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("Current plan");
  });

  it("renders plan names", () => {
    const { container } = render(<PlanManagerCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Pro");
    expect(container.textContent).toContain("Enterprise");
  });

  it("shows prices", () => {
    const { container } = render(<PlanManagerCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("$29/mo");
    expect(container.textContent).toContain("$99/mo");
  });

  it("renders feature lists", () => {
    const { container } = render(<PlanManagerCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("webhooks");
    expect(container.textContent).toContain("sso");
  });

  it("shows check marks for features", () => {
    const { container } = render(<PlanManagerCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("✓");
  });
});
