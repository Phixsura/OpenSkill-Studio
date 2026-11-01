import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitorCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-developer-api-api-endpoint-throughput-monitor-card";

const snapshots = [{ endpoint: "/api/users", rps: 500, peak_rps: 1200, avg_rps: 450 }];

describe("Card", () => {
  it("shows throughput", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitorCard snapshots={snapshots} appName="App" />);
    expect(container.textContent).toContain("Throughput Monitor");
    expect(container.textContent).toContain("500 rps");
    expect(container.textContent).toContain("peak: 1200");
    expect(container.textContent).toContain("avg: 450");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiEndpointThroughputMonitorCard snapshots={[]} appName="App" />);
    expect(container.textContent).toContain("No throughput data");
  });
});
