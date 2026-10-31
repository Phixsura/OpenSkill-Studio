import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FeatureAdoptionChart } from "@/components/feature-adoption-chart";

describe("FeatureAdoptionChart", () => {
  it("renders features", () => {
    const features = [
      { feature: "Search", unique_users: 800, adoption_pct: 80 },
      { feature: "Export", unique_users: 200, adoption_pct: 20 },
    ];
    const { container } = render(<FeatureAdoptionChart features={features} totalUsers={1000} />);
    expect(container.textContent).toContain("Search");
    expect(container.textContent).toContain("80%");
    expect(container.textContent).toContain("1,000 total users");
  });
});
