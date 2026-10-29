import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetricsCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-sandbox-metrics-card";

const sandboxes = [{ sandbox_id: "dev-sandbox", total_requests: 50000, unique_developers: 25, avg_response_ms: 45, error_rate: 1.5, health: "healthy", active: true }];

describe("Card", () => {
  it("shows sandbox metrics", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetricsCard sandboxes={sandboxes} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("Sandbox Metrics");
    expect(container.textContent).toContain("dev-sandbox");
    expect(container.textContent).toContain("50,000 reqs");
    expect(container.textContent).toContain("25 devs");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperSandboxMetricsCard sandboxes={[]} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No sandbox data");
  });
});
