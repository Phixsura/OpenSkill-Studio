import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder900 } from "@/components/milestone-under-900";
describe("MilestoneUnder900", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder900 />);
    expect(container.textContent).toContain("UNDER 900");
}); });
