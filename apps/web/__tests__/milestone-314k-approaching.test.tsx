import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone314kApproaching } from "@/components/milestone-314k-approaching";
describe("Milestone314kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone314kApproaching />);
    expect(container.textContent).toContain("314K");
}); });
