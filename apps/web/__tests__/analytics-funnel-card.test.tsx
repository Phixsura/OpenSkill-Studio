import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AnalyticsFunnelCard from "../src/components/analytics-funnel-card";

const steps = [
  { step_id: "visit", name: "Visit Page", entered: 1000, conversion_pct: 100, drop_off_pct: 0 },
  { step_id: "signup", name: "Sign Up", entered: 400, conversion_pct: 40, drop_off_pct: 60 },
  { step_id: "purchase", name: "Purchase", entered: 100, conversion_pct: 25, drop_off_pct: 75 },
];

describe("AnalyticsFunnelCard", () => {
  it("renders funnel name and app name", () => {
    const { container } = render(
      <AnalyticsFunnelCard
        funnelName="Onboarding"
        steps={steps}
        overallConversion={10}
        appName="My App"
      />,
    );
    expect(container.textContent).toContain("Onboarding");
    expect(container.textContent).toContain("My App");
  });

  it("shows overall conversion", () => {
    const { container } = render(
      <AnalyticsFunnelCard funnelName="F" steps={steps} overallConversion={10} appName="App" />,
    );
    expect(container.textContent).toContain("10% conversion");
  });

  it("renders step names", () => {
    const { container } = render(
      <AnalyticsFunnelCard funnelName="F" steps={steps} overallConversion={10} appName="App" />,
    );
    expect(container.textContent).toContain("Visit Page");
    expect(container.textContent).toContain("Sign Up");
    expect(container.textContent).toContain("Purchase");
  });

  it("shows user counts", () => {
    const { container } = render(
      <AnalyticsFunnelCard funnelName="F" steps={steps} overallConversion={10} appName="App" />,
    );
    expect(container.textContent).toContain("1.0K users");
    expect(container.textContent).toContain("400 users");
  });

  it("shows conversion percentages", () => {
    const { container } = render(
      <AnalyticsFunnelCard funnelName="F" steps={steps} overallConversion={10} appName="App" />,
    );
    expect(container.textContent).toContain("40%");
    expect(container.textContent).toContain("25%");
  });

  it("shows drop-off rates", () => {
    const { container } = render(
      <AnalyticsFunnelCard funnelName="F" steps={steps} overallConversion={10} appName="App" />,
    );
    expect(container.textContent).toContain("60% drop-off");
    expect(container.textContent).toContain("75% drop-off");
  });
});
