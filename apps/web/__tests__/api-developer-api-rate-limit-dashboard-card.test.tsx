import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIRateLimitDashboardCard from "../src/components/api-developer-api-rate-limit-dashboard-card";

const snapshots = [
  { endpoint: "/api/users", limit: 1000, remaining: 200, usage_pct: 80, consumer_id: "c1" },
  { endpoint: "/api/data", limit: 500, remaining: 400, usage_pct: 20, consumer_id: "c2" },
];

describe("APIDeveloperAPIRateLimitDashboardCard", () => {
  it("shows rate limit data", () => {
    const { container } = render(<APIDeveloperAPIRateLimitDashboardCard snapshots={snapshots} hotspotCount={1} appName="App" />);
    expect(container.textContent).toContain("Rate Limit Dashboard");
    expect(container.textContent).toContain("1 hotspots");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("200/1000");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIRateLimitDashboardCard snapshots={[]} hotspotCount={0} appName="App" />);
    expect(container.textContent).toContain("No rate limit data");
  });
});
