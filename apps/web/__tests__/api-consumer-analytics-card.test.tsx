import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIConsumerAnalyticsCard from "../src/components/api-consumer-analytics-card";

const consumers = [{ consumer_id: "app-1", total_requests: 5000, error_rate: 2.5, avg_latency_ms: 120 }];

describe("APIConsumerAnalyticsCard", () => {
  it("shows consumer stats", () => {
    const { container } = render(<APIConsumerAnalyticsCard consumers={consumers} appName="App" />);
    expect(container.textContent).toContain("Consumer Analytics");
    expect(container.textContent).toContain("app-1");
    expect(container.textContent).toContain("5000 reqs");
    expect(container.textContent).toContain("2.5% err");
  });
  it("shows empty", () => {
    const { container } = render(<APIConsumerAnalyticsCard consumers={[]} appName="App" />);
    expect(container.textContent).toContain("No consumer data");
  });
});
