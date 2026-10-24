import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone289kApproach } from "@/components/milestone-289k-approach";
describe("Milestone289kApproach", () => { it("renders", () => {
    const { container } = render(<Milestone289kApproach />);
    expect(container.textContent).toContain("289K");
}); });
