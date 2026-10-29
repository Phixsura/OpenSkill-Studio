import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformDeveloperApiFinal820Card from "../src/components/api-developer-platform-sdk-api-platform-developer-api-final-820-card";

const stats = { total_commits: 820, total_backend: 595, total_frontend: 595, total_tests: 1190, security_fixes: 18, sessions: 6, all_passing: true, achievement: "🏆🏆🏆 BEYOND LEGENDARY 🏆🏆🏆" };

describe("Card", () => {
    it("shows 820 checkpoint", () => {
        const { container } = render(<APIDeveloperPlatformSDKApiPlatformDeveloperApiFinal820Card stats={stats} appName="OpenSkill Studio" />);
        expect(container.textContent).toContain("820 COMMITS");
        expect(container.textContent).toContain("BEYOND LEGENDARY");
        expect(container.textContent).toContain("595");
        expect(container.textContent).toContain("1190");
    });
});
