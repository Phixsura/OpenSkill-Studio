import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-key-analytics-card";

describe("ApiKeyAnalyticsCard", () => {
  it("shows key stats", () => {
    const keys = [{ key_id: "k1", consumer_id: "c1", total_requests: 5000, error_rate: 2.5, endpoint_count: 8 }];
    const { container } = render(<Card keys={keys} totalKeys={3} appName="App" />);
    expect(container.textContent).toContain("Key Analytics");
    expect(container.textContent).toContain("k1");
    expect(container.textContent).toContain("5,000 reqs");
    expect(container.textContent).toContain("2.5% err");
  });
  it("shows empty", () => {
    const { container } = render(<Card keys={[]} totalKeys={0} appName="App" />);
    expect(container.textContent).toContain("No key analytics");
  });
});
