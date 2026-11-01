import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScoreCard from "../src/components/api-developer-api-api-developer-api-api-developer-experience-score-card";

const dx = { doc_coverage_pct: 95, onboarding_completion_pct: 90, uptime_pct: 99.99, avg_latency_ms: 45, nps: 80, avg_ticket_resolution_hours: 2, active_developers: 500, dx_score: 95, dx_grade: "A" };

describe("Card", () => {
    it("shows DX score", () => {
        const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperExperienceScoreCard dx={dx} appName="App" />);
        expect(container.textContent).toContain("Developer Experience");
        expect(container.textContent).toContain("A");
        expect(container.textContent).toContain("95/100");
        expect(container.textContent).toContain("99.99%");
        expect(container.textContent).toContain("500");
    });
});
