import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboardCard from "../src/components/api-developer-platform-sdk-api-platform-api-developer-api-usage-dashboard-card";

const dash = {
    total_requests_24h: 500000, total_requests_7d: 3000000, total_requests_30d: 12000000,
    unique_consumers_24h: 200, unique_endpoints: 50,
    avg_latency_ms: 45, p99_latency_ms: 200, error_rate_pct: 0.1,
    top_endpoint: "/api/users", top_consumer: "acme",
    webhook_deliveries_24h: 50000, cache_hit_rate_pct: 85,
    daily_growth_pct: 15, health: "excellent",
};

describe("Card", () => {
    it("shows usage dashboard", () => {
        const { container } = render(<APIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboardCard dashboard={dash} appName="App" />);
        expect(container.textContent).toContain("API Usage Dashboard");
        expect(container.textContent).toContain("EXCELLENT");
        expect(container.textContent).toContain("500,000");
        expect(container.textContent).toContain("+15%");
        expect(container.textContent).toContain("/api/users");
    });
});
