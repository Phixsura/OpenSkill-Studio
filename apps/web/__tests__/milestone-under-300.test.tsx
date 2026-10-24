import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder300 } from "@/components/milestone-under-300";
describe("MilestoneUnder300", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder300 />);
    expect(container.textContent).toContain("UNDER 300");
    expect(container.textContent).toContain("TWO MORE");
}); });
