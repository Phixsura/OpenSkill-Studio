import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder500 } from "@/components/milestone-under-500";
describe("MilestoneUnder500", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder500 />);
    expect(container.textContent).toContain("UNDER 500");
    expect(container.textContent).toContain("FIVE HUNDRED");
}); });
