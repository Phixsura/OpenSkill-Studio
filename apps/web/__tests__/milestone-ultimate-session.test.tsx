import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUltimateSession } from "@/components/milestone-ultimate-session";
describe("MilestoneUltimateSession", () => { it("renders", () => {
    const { container } = render(<MilestoneUltimateSession />);
    expect(container.textContent).toContain("ULTIMATE SESSION");
    expect(container.textContent).toContain("16,000+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
