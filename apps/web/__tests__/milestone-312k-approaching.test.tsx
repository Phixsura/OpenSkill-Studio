import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone312kApproaching } from "@/components/milestone-312k-approaching";
describe("Milestone312kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone312kApproaching />);
    expect(container.textContent).toContain("312K");
}); });
