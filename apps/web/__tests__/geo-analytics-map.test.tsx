import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GeoAnalyticsMap } from "@/components/geo-analytics-map";

describe("GeoAnalyticsMap", () => {
  const countries = [
    { country_code: "US", country_name: "United States", installs: 500, pct: 50 },
    { country_code: "GB", country_name: "United Kingdom", installs: 300, pct: 30 },
  ];
  it("renders", () => {
    const { container } = render(
      <GeoAnalyticsMap countries={countries} totalInstalls={1000}
        uniqueCountries={5} topCountry="US" />
    );
    expect(container.textContent).toContain("Geographic Distribution");
    expect(container.textContent).toContain("5 countries");
    expect(container.textContent).toContain("1,000 installs");
    expect(container.textContent).toContain("United States");
    expect(container.textContent).toContain("500");
    expect(container.textContent).toContain("50%");
  });
});
