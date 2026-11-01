import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDK850thCommitApproachingCard from "../src/components/api-developer-platform-sdk-850th-commit-approaching-card";

const progress = { total_backend: 620, total_frontend: 620, total_commits: 847, total_components: 1240, sessions: 8, security_fixes: 20, all_tests_passing: true, achievement: "🏆 TRANSCENDENT", avg_per_session: 155 };

describe("Card", () => {
    it("shows progress", () => {
        const { container } = render(<APIDeveloperPlatformSDK850thCommitApproachingCard progress={progress} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("Developer Platform SDK");
        expect(container.textContent).toContain("TRANSCENDENT");
        expect(container.textContent).toContain("620");
        expect(container.textContent).toContain("1240");
        expect(container.textContent).toContain("847");
    });
});
