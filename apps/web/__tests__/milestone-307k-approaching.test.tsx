import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone307kApproaching } from "@/components/milestone-307k-approaching";
describe("Milestone307kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone307kApproaching />);
    expect(container.textContent).toContain("307K");
}); });
