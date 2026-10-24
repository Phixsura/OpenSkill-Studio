import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder700 } from "@/components/milestone-under-700";
describe("MilestoneUnder700", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder700 />);
    expect(container.textContent).toContain("UNDER 700");
}); });
