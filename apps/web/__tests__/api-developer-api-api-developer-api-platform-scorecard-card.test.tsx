import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiPlatformScorecardCard from "../src/components/api-developer-api-api-developer-api-platform-scorecard-card";

const scorecard = {
    uptime_pct: 99.99, error_rate_pct: 0.01, avg_latency_ms: 45, p99_latency_ms: 200,
    webhook_delivery_rate_pct: 99.9, dead_letter_count: 5,
    security_score: 98, compliance_rate_pct: 100,
    nps: 75, active_developers: 500, total_api_calls_30d: 10000000,
    reliability_score: 99, performance_score: 100, security_grade: "A", overall_grade: "A",
};

describe("APIDeveloperAPIApiDeveloperApiPlatformScorecardCard", () => {
    it("shows the scorecard", () => {
        const { container } = render(<APIDeveloperAPIApiDeveloperApiPlatformScorecardCard scorecard={scorecard} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("Platform Scorecard");
        expect(container.textContent).toContain("A");
        expect(container.textContent).toContain("99.99%");
        expect(container.textContent).toContain("10,000,000");
        expect(container.textContent).toContain("500");
        expect(container.textContent).toContain("Reliability");
        expect(container.textContent).toContain("Performance");
    });
});
