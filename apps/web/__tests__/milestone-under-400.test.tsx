import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder400 } from "@/components/milestone-under-400";
describe("MilestoneUnder400", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder400 />);
    expect(container.textContent).toContain("UNDER 400");
    expect(container.textContent).toContain("THREE MORE");
}); });
