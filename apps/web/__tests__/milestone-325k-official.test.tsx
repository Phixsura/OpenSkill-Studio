import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone325kOfficial } from "@/components/milestone-325k-official";
describe("Milestone325kOfficial", () => { it("renders", () => {
    const { container } = render(<Milestone325kOfficial />);
    expect(container.textContent).toContain("325K OFFICIALLY CROSSED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
