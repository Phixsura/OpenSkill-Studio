import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone322kApproaching } from "@/components/milestone-322k-approaching";
describe("Milestone322kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone322kApproaching />);
    expect(container.textContent).toContain("322K");
}); });
