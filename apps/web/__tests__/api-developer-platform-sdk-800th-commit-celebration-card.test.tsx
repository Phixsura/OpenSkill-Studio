import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDK800thCommitCelebrationCard from "../src/components/api-developer-platform-sdk-800th-commit-celebration-card";

const celebration = {
    milestone: 800, total_backend: 575, total_frontend: 575, total_components: 1150,
    sessions_contributing: 5, security_fixes: 16, test_suites: 1150, all_passing: true,
    achievement: "🏆 ABSOLUTE LEGEND",
};

describe("Card", () => {
    it("shows 800th celebration", () => {
        const { container } = render(<APIDeveloperPlatformSDK800thCommitCelebrationCard celebration={celebration} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("800 COMMITS");
        expect(container.textContent).toContain("ABSOLUTE LEGEND");
        expect(container.textContent).toContain("575");
        expect(container.textContent).toContain("1150");
        expect(container.textContent).toContain("OpenSkill Studio");
    });
});
