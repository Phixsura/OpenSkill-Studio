import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3375288k } from "@/components/milestone-3375-288k";
describe("Milestone3375288k", () => { it("renders", () => {
    const { container } = render(<Milestone3375288k />);
    expect(container.textContent).toContain("UNSTOPPABLE");
}); });
