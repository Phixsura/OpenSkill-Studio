import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone309kApproaching } from "@/components/milestone-309k-approaching";
describe("Milestone309kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone309kApproaching />);
    expect(container.textContent).toContain("309K");
}); });
