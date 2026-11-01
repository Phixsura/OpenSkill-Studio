import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone324kApproaching } from "@/components/milestone-324k-approaching";
describe("Milestone324kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone324kApproaching />);
    expect(container.textContent).toContain("324K");
}); });
