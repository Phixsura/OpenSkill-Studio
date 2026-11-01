import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-api-consumer-api-uptime-monitor-card";

describe("UptimeMonitorCard", () => {
  it("shows uptime", () => {
    const endpoints = [{ endpoint: "/api", uptime_pct: 99.95, downtime_minutes: 2 }];
    const { container } = render(<Card endpoints={endpoints} slaBreachCount={0} appName="App" />);
    expect(container.textContent).toContain("Uptime Monitor");
    expect(container.textContent).toContain("/api");
    expect(container.textContent).toContain("99.95%");
  });
  it("shows SLA breach", () => {
    const endpoints = [{ endpoint: "/slow", uptime_pct: 98.5, downtime_minutes: 60 }];
    const { container } = render(<Card endpoints={endpoints} slaBreachCount={1} appName="App" />);
    expect(container.textContent).toContain("1 SLA breach");
  });
});
