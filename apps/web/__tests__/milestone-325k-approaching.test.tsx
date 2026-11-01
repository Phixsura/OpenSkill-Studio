import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone325kApproaching } from "@/components/milestone-325k-approaching";
describe("Milestone325kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone325kApproaching />);
    expect(container.textContent).toContain("325K");
}); });
