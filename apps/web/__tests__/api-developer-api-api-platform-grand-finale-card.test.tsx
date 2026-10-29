import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiPlatformGrandFinaleCard from "../src/components/api-developer-api-api-platform-grand-finale-card";

const finale = {
    total_services: 475, total_endpoints: 2000, total_developers: 1000, total_api_calls: 10000000,
    platform_grade: "A", uptime_pct: 99.99, avg_latency_ms: 45, error_rate_pct: 0.01,
    webhook_success_rate_pct: 99.9, total_webhook_deliveries: 500000,
    security_score: 100, compliance_rate_pct: 100,
    nps_score: 80, documentation_coverage_pct: 95,
    request_growth_pct: 25, developer_growth_pct: 15,
    overall_score: 98, verdict: "🏆 WORLD CLASS",
};

describe("APIDeveloperAPIApiPlatformGrandFinaleCard", () => {
    it("shows the grand finale", () => {
        const { container } = render(<APIDeveloperAPIApiPlatformGrandFinaleCard finale={finale} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("Developer Platform SDK");
        expect(container.textContent).toContain("475 services");
        expect(container.textContent).toContain("98");
        expect(container.textContent).toContain("WORLD CLASS");
        expect(container.textContent).toContain("99.99%");
        expect(container.textContent).toContain("10,000,000");
    });
});
