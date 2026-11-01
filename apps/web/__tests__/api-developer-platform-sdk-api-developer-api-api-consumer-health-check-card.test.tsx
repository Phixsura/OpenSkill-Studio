import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheckCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-consumer-health-check-card";

const checks = [
  { consumer_id: "acme", overall_health: "healthy", issue_count: 0, error_rate_pct: 0.1, auth_healthy: true, api_calls_healthy: true, webhook_healthy: true },
  { consumer_id: "beta", overall_health: "critical", issue_count: 2, error_rate_pct: 15, auth_healthy: false, api_calls_healthy: true, webhook_healthy: false },
];

describe("Card", () => {
  it("shows consumer health", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheckCard checks={checks} criticalCount={1} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("Consumer Health");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("acme");
    expect(container.textContent).toContain("healthy");
    expect(container.textContent).toContain("2 issues");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheckCard checks={[]} criticalCount={0} unhealthyCount={0} appName="App" />);
    expect(container.textContent).toContain("No consumer checks");
  });
});
