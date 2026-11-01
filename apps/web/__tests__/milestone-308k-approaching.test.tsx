import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone308kApproaching } from "@/components/milestone-308k-approaching";
describe("Milestone308kApproaching", () => { it("renders", () => {
    const { container } = render(<Milestone308kApproaching />);
    expect(container.textContent).toContain("308K");
}); });
