import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone290kApproaching } from "@/components/milestone-290k-approaching";
describe("Milestone290kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone290kApproaching />);
    expect(container.textContent).toContain("290,000 LINES");
}); });
