import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-api-api-consumer-api-api-consumer-api-api-api-consumer-api-api-consumer-api-api-latency-tracker-card";

describe("LatencyTrackerCard", () => {
  it("shows distribution", () => {
    const buckets = [{ label: "<50ms", count: 50 }, { label: "50-100ms", count: 30 }, { label: "100-500ms", count: 15 }, { label: "500ms-1s", count: 4 }, { label: ">1s", count: 1 }];
    const { container } = render(<Card consumerId="c1" totalRequests={100} p50={45} p95={350} p99={800} avg={120} buckets={buckets} appName="App" />);
    expect(container.textContent).toContain("Latency Distribution");
    expect(container.textContent).toContain("45ms");
    expect(container.textContent).toContain("350ms");
    expect(container.textContent).toContain("P99");
  });
  it("shows zero", () => {
    const { container } = render(<Card consumerId="c1" totalRequests={0} p50={0} p95={0} p99={0} avg={0} buckets={[]} appName="App" />);
    expect(container.textContent).toContain("0");
  });
});
