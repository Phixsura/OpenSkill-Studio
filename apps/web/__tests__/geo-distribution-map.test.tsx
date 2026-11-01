import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GeoDistributionMap } from "@/components/geo-distribution-map";

describe("GeoDistributionMap", () => {
  it("renders geo data", () => {
    const { container } = render(
      <GeoDistributionMap total={100} topRegion="us-east"
        distribution={[
          { region: "us-east", name: "US East", count: 50, pct: 50 },
          { region: "eu-west", name: "EU West", count: 30, pct: 30 },
          { region: "ap-southeast", name: "Asia Pacific SE", count: 20, pct: 20 },
        ]} />
    );
    expect(container.textContent).toContain("Geo Distribution");
    expect(container.textContent).toContain("100 requests");
    expect(container.textContent).toContain("US East");
    expect(container.textContent).toContain("50%");
    expect(container.textContent).toContain("top");
  });
});
