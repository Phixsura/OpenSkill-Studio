import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone15kApproaching } from "@/components/milestone-15k-approaching";
describe("Milestone15kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone15kApproaching />);
    expect(container.textContent).toContain("15K");
}); });
