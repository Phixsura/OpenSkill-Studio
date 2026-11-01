import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone317kApproaching } from "@/components/milestone-317k-approaching";
describe("Milestone317kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone317kApproaching />);
    expect(container.textContent).toContain("317K");
}); });
