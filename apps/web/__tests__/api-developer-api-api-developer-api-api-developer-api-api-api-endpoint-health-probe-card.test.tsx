import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbeCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-api-endpoint-health-probe-card";

const probes = [
  { endpoint: "/health", success_rate: 99.5, consecutive_failures: 0, last_status: 200, last_response_ms: 15 },
  { endpoint: "/api/db", success_rate: 85, consecutive_failures: 3, last_status: 500, last_response_ms: 5000 },
];

describe("Card", () => {
  it("shows probes", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbeCard probes={probes} unhealthyCount={1} appName="App" />);
    expect(container.textContent).toContain("Health Probes");
    expect(container.textContent).toContain("1 unhealthy");
    expect(container.textContent).toContain("/health");
    expect(container.textContent).toContain("99.5%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiEndpointHealthProbeCard probes={[]} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No health probes");
  });
});
