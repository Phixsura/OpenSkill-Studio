import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone289kCrossed290k } from "@/components/milestone-289k-crossed-290k";
describe("Milestone289kCrossed290k", () => { it("renders", () => {
    const { container } = render(<Milestone289kCrossed290k />);
    expect(container.textContent).toContain("289K+");
    expect(container.textContent).toContain("290,000");
}); });
