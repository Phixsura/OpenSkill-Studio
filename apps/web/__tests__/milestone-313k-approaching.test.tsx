import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone313kApproaching } from "@/components/milestone-313k-approaching";
describe("Milestone313kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone313kApproaching />);
    expect(container.textContent).toContain("313K");
}); });
