import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiEndpointErrorRateMonitorCard from "../src/components/api-developer-platform-sdk-api-endpoint-error-rate-monitor-card";

const endpoints = [
  { endpoint: "/api/payments", error_rate_pct: 12.5, total_requests: 1000, status: "critical", last_error_code: "TIMEOUT" },
  { endpoint: "/api/users", error_rate_pct: 0.5, total_requests: 50000, status: "normal", last_error_code: "" },
];

describe("Card", () => {
  it("shows error rates", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointErrorRateMonitorCard endpoints={endpoints} overallRate={2.1} criticalCount={1} appName="App" />);
    expect(container.textContent).toContain("Error Rates");
    expect(container.textContent).toContain("overall: 2.1%");
    expect(container.textContent).toContain("1 critical");
    expect(container.textContent).toContain("/api/payments");
    expect(container.textContent).toContain("12.5%");
  });
  it("shows empty", () => {
    const { container } = render(<APIDeveloperPlatformSDKApiEndpointErrorRateMonitorCard endpoints={[]} overallRate={0} criticalCount={0} appName="App" />);
    expect(container.textContent).toContain("No error data");
  });
});
