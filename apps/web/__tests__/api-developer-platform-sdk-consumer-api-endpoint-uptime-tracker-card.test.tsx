import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Card from "../src/components/api-developer-platform-sdk-consumer-api-endpoint-uptime-tracker-card";

describe("EndpointUptimeTrackerCard", () => {
  it("shows reports", () => {
    const reports = [{ endpoint: "/api/users", uptimePct: 99.95, totalChecks: 1000, upCount: 999, downCount: 1, avgMs: 75, currentStatus: "up", downtimeMin: 1 }];
    const { container } = render(<Card reports={reports} appName="App" />);
    expect(container.textContent).toContain("Uptime Tracker");
    expect(container.textContent).toContain("/api/users");
    expect(container.textContent).toContain("99.95%");
    expect(container.textContent).toContain("1 outages");
  });
  it("shows empty", () => {
    const { container } = render(<Card reports={[]} appName="App" />);
    expect(container.textContent).toContain("No uptime data");
  });
});
