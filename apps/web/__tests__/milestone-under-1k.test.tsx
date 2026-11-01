import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder1k } from "@/components/milestone-under-1k";
describe("MilestoneUnder1k", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder1k />);
    expect(container.textContent).toContain("UNDER 1,000");
    expect(container.textContent).toContain("NINE HUNDRED");
}); });
