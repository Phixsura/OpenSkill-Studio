import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIKeyAnalyticsCard from "../src/components/api-developer-api-key-analytics-card";

const keys = [{ key_id: "k1", total_requests: 5000, error_rate: 2.5, avg_latency_ms: 120, top_endpoint: "/api/users" }];

describe("APIDeveloperAPIKeyAnalyticsCard", () => {
  it("shows key analytics", () => {
    const { container } = render(<APIDeveloperAPIKeyAnalyticsCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("Key Analytics");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("5000 reqs");
    expect(container.textContent).toContain("2.5% err");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIKeyAnalyticsCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No key analytics");
  });
});
