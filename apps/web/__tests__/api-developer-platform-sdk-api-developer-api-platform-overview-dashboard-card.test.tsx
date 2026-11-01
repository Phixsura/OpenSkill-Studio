import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboardCard from "../src/components/api-developer-platform-sdk-api-developer-api-platform-overview-dashboard-card";

const overview = {
    total_services: 563, total_consumers: 500, total_api_calls_today: 1000000,
    platform_health: "healthy", health_emoji: "🟢", uptime_pct: 99.99, avg_latency_ms: 45, error_rate_pct: 0.1,
    webhook_success_rate: 99.9, active_destinations: 50, queue_depth: 10,
    security_score: 100, active_api_keys: 200,
    nps: 75, active_developers: 300, support_tickets_open: 5,
    consumer_growth_pct: 15, revenue_mrr_cents: 500000, overall_score: 100,
};

describe("Card", () => {
    it("shows platform overview", () => {
        const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiPlatformOverviewDashboardCard overview={overview} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("Platform Overview");
        expect(container.textContent).toContain("563 services");
        expect(container.textContent).toContain("100");
        expect(container.textContent).toContain("99.99%");
        expect(container.textContent).toContain("1,000,000");
        expect(container.textContent).toContain("$5000");
    });
});
