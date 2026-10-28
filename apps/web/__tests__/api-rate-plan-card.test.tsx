import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIRatePlanCard from "../src/components/api-rate-plan-card";

const plans = [
  {
    plan_id: "free",
    name: "Free",
    requests_per_minute: 60,
    requests_per_hour: 1000,
    requests_per_day: 10000,
  },
  {
    plan_id: "pro",
    name: "Pro",
    requests_per_minute: 300,
    requests_per_hour: 10000,
    requests_per_day: 100000,
  },
];

describe("APIRatePlanCard", () => {
  it("renders header and plan count", () => {
    const { container } = render(<APIRatePlanCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("Rate Plans");
    expect(container.textContent).toContain("2 plans");
  });

  it("shows plan names", () => {
    const { container } = render(<APIRatePlanCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("Free");
    expect(container.textContent).toContain("Pro");
  });

  it("shows rate limits", () => {
    const { container } = render(<APIRatePlanCard plans={plans} appName="App" />);
    expect(container.textContent).toContain("60/min");
    expect(container.textContent).toContain("10,000/hr");
    expect(container.textContent).toContain("100,000/day");
  });

  it("shows empty state", () => {
    const { container } = render(<APIRatePlanCard plans={[]} appName="App" />);
    expect(container.textContent).toContain("No rate plans");
  });
});
