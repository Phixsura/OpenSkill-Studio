import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDK600thServicePairCard from "../src/components/api-developer-platform-sdk-600th-service-pair-card";

const milestone = {
    total_backend: 600, total_frontend: 600, total_components: 1200,
    total_commits: 826, total_tests: 1200, sessions: 7,
    security_fixes: 19, all_passing: true, achievement: "🏆🏆🏆 TRANSCENDENT 🏆🏆🏆",
};

describe("Card", () => {
    it("shows 600th pair milestone", () => {
        const { container } = render(<APIDeveloperPlatformSDK600thServicePairCard milestone={milestone} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("600 SERVICE PAIRS");
        expect(container.textContent).toContain("TRANSCENDENT");
        expect(container.textContent).toContain("600");
        expect(container.textContent).toContain("1200");
        expect(container.textContent).toContain("826");
        expect(container.textContent).toContain("ALL PASS");
    });
});
