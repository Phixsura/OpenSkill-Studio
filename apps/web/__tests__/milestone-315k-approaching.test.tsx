import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone315kApproaching } from "@/components/milestone-315k-approaching";
describe("Milestone315kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone315kApproaching />);
    expect(container.textContent).toContain("315K");
}); });
