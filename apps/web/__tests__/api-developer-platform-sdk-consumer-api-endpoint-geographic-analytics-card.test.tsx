import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-geographic-analytics-card";

describe("GeographicAnalyticsCard", () => {
  it("shows geo data", () => {
    const countries = [{ code: "US", region: "NA", requests: 5000, avgMs: 50, errors: 10 }, { code: "AU", region: "APAC", requests: 1000, avgMs: 300, errors: 5 }];
    const { container } = render(<Card countries={countries} byRegion={{ NA: 5000, APAC: 1000 }} totalRequests={6000} uniqueCountries={2} highestLatency="AU" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("Geographic Analytics");
    expect(container.textContent).toContain("NA: 5,000");
    expect(container.textContent).toContain("AU");
    expect(container.textContent).toContain("🐌");
  });
  it("shows empty", () => {
    const { container } = render(<Card countries={[]} byRegion={{}} totalRequests={0} uniqueCountries={0} highestLatency="" consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("No geographic data");
  });
});
