import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MilestoneUnder200 } from "@/components/milestone-under-200";
describe("MilestoneUnder200", () => { it("renders", () => {
    const { container } = render(<MilestoneUnder200 />);
    expect(container.textContent).toContain("UNDER 200");
    expect(container.textContent).toContain("ONE. MORE. BATCH.");
}); });
