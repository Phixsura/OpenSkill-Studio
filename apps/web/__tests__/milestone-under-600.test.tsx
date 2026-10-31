import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder600 } from "@/components/milestone-under-600";
describe("MilestoneUnder600", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder600 />);
    expect(container.textContent).toContain("UNDER 600");
}); });
