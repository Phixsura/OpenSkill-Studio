import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPISLATrackerCard from "../src/components/api-developer-api-sla-tracker-card";

const slas = [
  { service_name: "API", uptime_target: 99.9, current_uptime: 99.95, latency_target_ms: 200, current_p95_ms: 150, sla_met: true },
  { service_name: "DB", uptime_target: 99.99, current_uptime: 99.5, latency_target_ms: 50, current_p95_ms: 80, sla_met: false },
];

describe("APIDeveloperAPISLATrackerCard", () => {
  it("shows SLAs with violations", () => {
    const { container } = render(<APIDeveloperAPISLATrackerCard slas={slas} appName="App" />);
    expect(container.textContent).toContain("SLA Tracker");
    expect(container.textContent).toContain("1 violated");
    expect(container.textContent).toContain("API");
    expect(container.textContent).toContain("99.95%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPISLATrackerCard slas={[]} appName="App" />);
    expect(container.textContent).toContain("No SLAs configured");
  });
});
