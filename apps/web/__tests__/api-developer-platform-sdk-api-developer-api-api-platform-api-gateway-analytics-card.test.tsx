import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalyticsCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-platform-api-gateway-analytics-card";

const analytics = { total_requests: 1000000, error_rate_pct: 0.05, avg_latency_ms: 30, p99_latency_ms: 150, cache_hit_rate_pct: 85, rate_limited_requests: 500, auth_failures: 100, health: "excellent" };

describe("Card", () => {
    it("shows gateway analytics", () => {
        const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalyticsCard analytics={analytics} appName="App" />);
        expect(container.textContent).toContain("Gateway Analytics");
        expect(container.textContent).toContain("EXCELLENT");
        expect(container.textContent).toContain("1,000,000");
        expect(container.textContent).toContain("0.05%");
        expect(container.textContent).toContain("85%");
    });
});
