import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiFinalSummaryCard from "../src/components/api-developer-api-api-developer-api-api-developer-api-api-developer-api-final-summary-card";

const summary = {
    total_backend_services: 530, total_frontend_components: 530,
    total_commits: 750, total_security_fixes: 14, total_test_suites: 1060,
    dimension_count: 10, verdict: "🏆 LEGENDARY ACHIEVEMENT", all_tests_passing: true,
};

describe("Card", () => {
    it("shows final summary", () => {
        const { container } = render(<APIDeveloperAPIApiDeveloperApiApiDeveloperApiApiFinalSummaryCard summary={summary} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("Developer Platform SDK");
        expect(container.textContent).toContain("LEGENDARY ACHIEVEMENT");
        expect(container.textContent).toContain("530");
        expect(container.textContent).toContain("750");
        expect(container.textContent).toContain("ALL TESTS PASSING");
    });
});
