import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FeatureGateCard from "../src/components/feature-gate-card";

const gates = [
  {
    gate_id: "g1",
    name: "Premium Feature",
    condition_count: 2,
    match_all: true,
    eval_count: 100,
    pass_rate: 75,
  },
  {
    gate_id: "g2",
    name: "Beta Access",
    condition_count: 1,
    match_all: false,
    eval_count: 50,
    pass_rate: 30,
  },
];

describe("FeatureGateCard", () => {
  it("renders header", () => {
    const { container } = render(<FeatureGateCard gates={gates} appName="My App" />);
    expect(container.textContent).toContain("Feature Gates");
  });

  it("shows gate count", () => {
    const { container } = render(<FeatureGateCard gates={gates} appName="App" />);
    expect(container.textContent).toContain("2 gates");
  });

  it("renders gate names", () => {
    const { container } = render(<FeatureGateCard gates={gates} appName="App" />);
    expect(container.textContent).toContain("Premium Feature");
    expect(container.textContent).toContain("Beta Access");
  });

  it("shows condition count and mode", () => {
    const { container } = render(<FeatureGateCard gates={gates} appName="App" />);
    expect(container.textContent).toContain("2 conditions · AND");
    expect(container.textContent).toContain("1 conditions · OR");
  });

  it("shows pass rate and evaluations", () => {
    const { container } = render(<FeatureGateCard gates={gates} appName="App" />);
    expect(container.textContent).toContain("75% pass");
    expect(container.textContent).toContain("100 evaluations");
  });

  it("shows empty state", () => {
    const { container } = render(<FeatureGateCard gates={[]} appName="App" />);
    expect(container.textContent).toContain("No feature gates");
  });
});
