import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-request-ip-reputation-card";

describe("RequestIpReputationCard", () => {
  it("shows reputations", () => {
    const reps = [{ ip_address: "10.0.0.1", score: 95, tier: "trusted", total_requests: 1000, suspicious_events: 0 }];
    const { container } = render(<Card reputations={reps} suspiciousCount={0} appName="App" />);
    expect(container.textContent).toContain("IP Reputation");
    expect(container.textContent).toContain("10.0.0.1");
    expect(container.textContent).toContain("trusted");
  });
  it("shows suspicious count", () => {
    const { container } = render(<Card reputations={[]} suspiciousCount={5} appName="App" />);
    expect(container.textContent).toContain("5 suspicious");
  });
});
