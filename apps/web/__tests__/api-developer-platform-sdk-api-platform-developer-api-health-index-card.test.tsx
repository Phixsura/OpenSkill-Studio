import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import APIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndexCard from "../src/components/api-developer-platform-sdk-api-platform-developer-api-health-index-card";

const health = { index: 95.5, grade: "A+", trend_emoji: "🟢", availability_score: 99, latency_score: 95, error_rate_score: 98, webhook_score: 97, security_score: 90, dx_score: 85 };

describe("Card", () => {
    it("shows health index", () => {
        const { container } = render(<APIDeveloperPlatformSDKApiPlatformDeveloperApiHealthIndexCard health={health} appName="OpenSkill" />);
        expect(container.textContent).toContain("Platform Health Index");
        expect(container.textContent).toContain("A+");
        expect(container.textContent).toContain("95.5/100");
        expect(container.textContent).toContain("99");
        expect(container.textContent).toContain("Availability");
    });
});
