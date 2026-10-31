import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiKeyAnalyticsCard from "../src/components/api-developer-api-api-key-analytics-card";

const keys = [
  { key_id: "k1", key_prefix: "sk-abcd", total_requests: 1500, error_count: 3, endpoints_hit: { "/api/a": 1000, "/api/b": 500 } },
  { key_id: "k2", key_prefix: "sk-efgh", total_requests: 200, error_count: 0, endpoints_hit: { "/api/c": 200 } },
];

describe("APIDeveloperAPIApiKeyAnalyticsCard", () => {
  it("shows key analytics", () => {
    const { container } = render(<APIDeveloperAPIApiKeyAnalyticsCard keys={keys} appName="App" />);
    expect(container.textContent).toContain("API Key Analytics");
    expect(container.textContent).toContain("2 keys tracked");
    expect(container.textContent).toContain("sk-abcd");
    expect(container.textContent).toContain("1,500 reqs");
    expect(container.textContent).toContain("3 errors");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiKeyAnalyticsCard keys={[]} appName="App" />);
    expect(container.textContent).toContain("No API key usage");
  });
});
