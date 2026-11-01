import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone12kApproach } from "@/components/milestone-12k-approach";
describe("Milestone12kApproach", () => { it("renders", () => {
    const { container } = render(<Milestone12kApproach />);
    expect(container.textContent).toContain("12,000 Files");
}); });
