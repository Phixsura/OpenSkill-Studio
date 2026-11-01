import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiEndpointTrafficAnalyzerCard from "../src/components/api-developer-platform-sdk-api-endpoint-traffic-analyzer-card";

const traffic = [{ endpoint: "/api/users", method: "GET", total_requests: 500000, unique_consumers: 200, traffic_tier: "high", peak_rps: 500 }];

describe("Card", () => {
  it("shows traffic", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointTrafficAnalyzerCard traffic={traffic} tierCounts={{ high: 1 }} appName="App" />);
    expect(container.textContent).toContain("Traffic Analyzer");
    expect(container.textContent).toContain("GET");
    expect(container.textContent).toContain("500,000");
    expect(container.textContent).toContain("high: 1");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointTrafficAnalyzerCard traffic={[]} tierCounts={{}} appName="App" />);
    expect(container.textContent).toContain("No traffic data");
  });
});
