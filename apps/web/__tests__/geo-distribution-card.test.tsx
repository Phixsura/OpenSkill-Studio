import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GeoDistributionCard } from "@/components/geo-distribution-card";

describe("GeoDistributionCard", () => {
  it("renders regions", () => {
    const { container } = render(
      <GeoDistributionCard total={100} topRegion="us-east" regions={[
        { region: "us-east", label: "US East", count: 50, pct: 50 },
        { region: "eu-west", label: "Europe West", count: 30, pct: 30 },
        { region: "ap-east", label: "Asia Pacific", count: 20, pct: 20 },
      ]} />
    );
    expect(container.textContent).toContain("Traffic Distribution");
    expect(container.textContent).toContain("100");
    expect(container.textContent).toContain("US East");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("Europe West");
  });
});
