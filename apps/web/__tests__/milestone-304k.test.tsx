import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone304k } from "@/components/milestone-304k";
describe("Milestone304k", () => { it("renders", () => {
    const { container } = render(<Milestone304k />);
    expect(container.textContent).toContain("304K");
    expect(container.textContent).toContain("UNSTOPPABLE");
}); });
