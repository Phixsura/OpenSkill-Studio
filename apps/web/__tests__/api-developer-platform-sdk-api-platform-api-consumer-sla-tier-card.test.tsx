import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiConsumerSLATierCard from "../src/components/api-developer-platform-sdk-api-platform-api-consumer-sla-tier-card";

const consumers = [
  { consumer_id: "acme", tier: "platinum", uptime_target: 99.99, actual_uptime: 99.995, latency_target_ms: 100, actual_latency_ms: 80, meeting_sla: true },
  { consumer_id: "beta", tier: "gold", uptime_target: 99.9, actual_uptime: 99.0, latency_target_ms: 200, actual_latency_ms: 500, meeting_sla: false },
];

describe("Card", () => {
  it("shows SLA tiers", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerSLATierCard consumers={consumers} tierCounts={{ platinum: 1, gold: 1 }} breachingCount={1} appName="App" />);
    expect(container.textContent).toContain("SLA Tiers");
    expect(container.textContent).toContain("1 breaching");
    expect(container.textContent).toContain("platinum");
    expect(container.textContent).toContain("acme");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiConsumerSLATierCard consumers={[]} tierCounts={{}} breachingCount={0} appName="App" />);
    expect(container.textContent).toContain("No SLA data");
  });
});
