import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiDeveloperApiApiWebhookDeliveryAnalyticsDashboardCard from "../src/components/api-developer-platform-sdk-api-developer-api-api-webhook-delivery-analytics-dashboard-card";

const dash = { total_deliveries: 500000, success_rate: 99.9, retry_rate: 0.5, avg_latency_ms: 45, p99_latency_ms: 200, active_destinations: 50, dead_letters: 5, queue_depth: 20, health: "excellent" };

describe("Card", () => {
    it("shows analytics dashboard", () => {
        const { container } = render(<APIDeveloperPlatformSDKApiDeveloperApiApiWebhookDeliveryAnalyticsDashboardCard dashboard={dash} appName="App" />);
        expect(container.textContent).toContain("Delivery Analytics");
        expect(container.textContent).toContain("EXCELLENT");
        expect(container.textContent).toContain("500,000");
        expect(container.textContent).toContain("99.9%");
        expect(container.textContent).toContain("200");
    });
});
