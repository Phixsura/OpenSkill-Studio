import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import ABTestCard from "../src/components/ab-test-card";

const experiments = [
  {
    experiment_id: "exp1",
    name: "Button Color",
    active: true,
    variants: [
      { name: "control", impressions: 500, conversions: 50, rate: 10.0 },
      { name: "treatment", impressions: 500, conversions: 75, rate: 15.0 },
    ],
  },
  {
    experiment_id: "exp2",
    name: "Pricing Page",
    active: false,
    variants: [
      { name: "A", impressions: 200, conversions: 20, rate: 10.0 },
      { name: "B", impressions: 200, conversions: 30, rate: 15.0 },
    ],
  },
];

describe("ABTestCard", () => {
  it("renders header and counts", () => {
    const { container } = render(<ABTestCard experiments={experiments} appName="App" />);
    expect(container.textContent).toContain("A/B Tests");
    expect(container.textContent).toContain("1 active / 2 total");
  });

  it("shows experiment names", () => {
    const { container } = render(<ABTestCard experiments={experiments} appName="App" />);
    expect(container.textContent).toContain("Button Color");
    expect(container.textContent).toContain("Pricing Page");
  });

  it("shows variant rates", () => {
    const { container } = render(<ABTestCard experiments={experiments} appName="App" />);
    expect(container.textContent).toContain("10%");
    expect(container.textContent).toContain("15%");
  });

  it("shows active/ended status", () => {
    const { container } = render(<ABTestCard experiments={experiments} appName="App" />);
    expect(container.textContent).toContain("active");
    expect(container.textContent).toContain("ended");
  });

  it("shows empty state", () => {
    const { container } = render(<ABTestCard experiments={[]} appName="App" />);
    expect(container.textContent).toContain("No experiments");
  });
});
