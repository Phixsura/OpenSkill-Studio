import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformAchievementTracker } from "@/components/platform-achievement-tracker";
describe("PlatformAchievementTracker", () => { it("renders", () => {
    const { container } = render(<PlatformAchievementTracker />);
    expect(container.textContent).toContain("27 ACHIEVEMENTS");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
