import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone324kOfficial } from "@/components/milestone-324k-official";
describe("Milestone324kOfficial", () => { it("renders", () => {
    const { container } = render(<Milestone324kOfficial />);
    expect(container.textContent).toContain("324K OFFICIALLY CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
