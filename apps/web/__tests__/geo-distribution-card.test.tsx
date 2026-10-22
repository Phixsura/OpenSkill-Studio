import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GeoDistributionCard } from "@/components/geo-distribution-card";

describe("GeoDistributionCard", () => {
  it("renders countries", () => {
    const { container } = render(
      <GeoDistributionCard countries={[{ country: "US", count: 500 }, { country: "DE", count: 200 }]} totalInstalls={700} />
    );
    expect(container.textContent).toContain("US");
    expect(container.textContent).toContain("DE");
    expect(container.textContent).toContain("700");
  });
  it("shows flags", () => {
    const { container } = render(
      <GeoDistributionCard countries={[{ country: "JP", count: 100 }]} totalInstalls={100} />
    );
    expect(container.textContent).toContain("🇯🇵");
  });
});
