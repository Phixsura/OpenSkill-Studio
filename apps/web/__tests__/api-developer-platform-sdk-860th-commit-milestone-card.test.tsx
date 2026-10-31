import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDK860thCommitMilestoneCard from "../src/components/api-developer-platform-sdk-860th-commit-milestone-card";

const milestone = { total_backend: 631, total_frontend: 631, total_components: 1262, total_commits: 860, sessions: 9, all_passing: true, achievement: "🏆🏆🏆 GODLIKE 🏆🏆🏆" };

describe("Card", () => {
    it("shows 860 milestone", () => {
        const { container } = render(<APIDeveloperPlatformSDK860thCommitMilestoneCard milestone={milestone} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("860 COMMITS");
        expect(container.textContent).toContain("GODLIKE");
        expect(container.textContent).toContain("631");
        expect(container.textContent).toContain("1262");
        expect(container.textContent).toContain("ALL TESTS PASSING");
    });
});
