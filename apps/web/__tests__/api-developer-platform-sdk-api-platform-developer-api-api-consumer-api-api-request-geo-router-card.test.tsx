import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-request-geo-router-card";

describe("RequestGeoRouterCard", () => {
  it("shows backends", () => {
    const backends = [{ region: "us-east", healthy: true, latency_ms: 20, load_pct: 45 }];
    const { container } = render(<Card backends={backends} defaultRegion="us-east" healthyRegionCount={2} appName="App" />);
    expect(container.textContent).toContain("Geo Router");
    expect(container.textContent).toContain("us-east");
    expect(container.textContent).toContain("45% load");
    expect(container.textContent).toContain("2 regions up");
  });
  it("shows empty", () => {
    const { container } = render(<Card backends={[]} defaultRegion="us-east" healthyRegionCount={0} appName="App" />);
    expect(container.textContent).toContain("No backends");
  });
});
