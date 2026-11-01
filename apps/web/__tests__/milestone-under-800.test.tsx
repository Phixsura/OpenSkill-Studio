import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder800 } from "@/components/milestone-under-800";
describe("MilestoneUnder800", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder800 />);
    expect(container.textContent).toContain("UNDER 800");
}); });
