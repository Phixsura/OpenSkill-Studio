import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-api-consumer-api-consumer-sla-tier-card";

describe("ConsumerSlaTierCard", () => {
  it("shows tier and compliance", () => {
    const tier = { id: "gold", name: "Gold", uptimePct: 99.9, maxLatencyMs: 200, maxErrorRatePct: 0.1, supportHours: 4 };
    const { container } = render(<Card tier={tier} compliance={{ uptimeOk: true, latencyOk: true, errorRateOk: true }} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("SLA Tier");
    expect(container.textContent).toContain("Gold");
    expect(container.textContent).toContain("99.9%");
    expect(container.textContent).toContain("All SLA targets met");
  });
  it("shows breach", () => {
    const tier = { id: "gold", name: "Gold", uptimePct: 99.9, maxLatencyMs: 200, maxErrorRatePct: 0.1, supportHours: 4 };
    const { container } = render(<Card tier={tier} compliance={{ uptimeOk: false, latencyOk: true, errorRateOk: true }} consumerId="c1" appName="App" />);
    expect(container.textContent).toContain("SLA breach detected");
  });
});
