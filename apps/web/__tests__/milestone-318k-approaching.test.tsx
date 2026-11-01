import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone318kApproaching } from "@/components/milestone-318k-approaching";
describe("Milestone318kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone318kApproaching />);
    expect(container.textContent).toContain("318K");
}); });
