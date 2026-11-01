import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GeoMapSummary } from "@/components/geo-map-summary";

describe("GeoMapSummary", () => {
  const distribution = [{ country: "US", count: 50 }, { country: "AU", count: 30 }];
  it("renders distribution", () => {
    const { container } = render(<GeoMapSummary distribution={distribution} totalIps={80} countries={2} />);
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("AU");
    expect(container.textContent).toContain("2 countries");
    expect(container.textContent).toContain("80 IPs");
  });
});
