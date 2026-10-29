import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalyticsCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-api-api-request-geo-analytics-card";

const regions = [
  { region: "NA", request_count: 50000, avg_latency_ms: 45, error_rate: 0.1 },
  { region: "APAC", request_count: 20000, avg_latency_ms: 200, error_rate: 0.5 },
];

describe("Card", () => {
  it("shows geo analytics", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalyticsCard regions={regions} totalRequests={70000} appName="App" />);
    expect(container.textContent).toContain("Geo Analytics");
    expect(container.textContent).toContain("70,000 total");
    expect(container.textContent).toContain("NA");
    expect(container.textContent).toContain("50,000");
    expect(container.textContent).toContain("200ms");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiApiRequestGeoAnalyticsCard regions={[]} totalRequests={0} appName="App" />);
    expect(container.textContent).toContain("No geo data");
  });
});
