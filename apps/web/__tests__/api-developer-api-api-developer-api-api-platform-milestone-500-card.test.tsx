import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperAPIApiDeveloperApiApiPlatformMilestone500Card from "../src/components/api-developer-api-api-developer-api-api-platform-milestone-500-card";

const milestone = {
    total_backend_services: 500, total_frontend_components: 500,
    total_test_suites: 1000, total_commits: 720, security_fixes: 12,
    milestone_grade: "🏆 LEGENDARY", coverage_completeness: 100,
};

describe("APIDeveloperAPIApiDeveloperApiApiPlatformMilestone500Card", () => {
    it("shows the 500 milestone", () => {
        const { container } = render(<APIDeveloperAPIApiDeveloperApiApiPlatformMilestone500Card milestone={milestone} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("500 SERVICES MILESTONE");
        expect(container.textContent).toContain("LEGENDARY");
        expect(container.textContent).toContain("500");
        expect(container.textContent).toContain("720");
        expect(container.textContent).toContain("100%");
    });
});
