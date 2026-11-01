import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import FeatureUsageCard from "../src/components/feature-usage-card";

const features = [
  { feature_id: "dashboard", unique_users: 80, total_uses: 5000, adoption_pct: 80 },
  { feature_id: "api_explorer", unique_users: 30, total_uses: 500, adoption_pct: 30 },
  { feature_id: "dark_mode", unique_users: 10, total_uses: 50, adoption_pct: 10 },
];

describe("FeatureUsageCard", () => {
  it("renders header", () => {
    const { container } = render(
      <FeatureUsageCard features={features} totalUsers={100} appName="My App" />,
    );
    expect(container.textContent).toContain("Feature Usage");
    expect(container.textContent).toContain("My App");
  });

  it("shows user and feature counts", () => {
    const { container } = render(
      <FeatureUsageCard features={features} totalUsers={100} appName="App" />,
    );
    expect(container.textContent).toContain("100 users");
    expect(container.textContent).toContain("3 features");
  });

  it("renders feature names", () => {
    const { container } = render(
      <FeatureUsageCard features={features} totalUsers={100} appName="App" />,
    );
    expect(container.textContent).toContain("dashboard");
    expect(container.textContent).toContain("api explorer");
  });

  it("shows adoption and usage", () => {
    const { container } = render(
      <FeatureUsageCard features={features} totalUsers={100} appName="App" />,
    );
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("5.0K uses");
  });

  it("shows empty state", () => {
    const { container } = render(<FeatureUsageCard features={[]} totalUsers={0} appName="App" />);
    expect(container.textContent).toContain("No feature usage data");
  });
});
