import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3440 } from "@/components/milestone-3440";
describe("Milestone3440", () => { it("renders", () => {
    const { container } = render(<Milestone3440 />);
    expect(container.textContent).toContain("3,440");
    expect(container.textContent).toContain("4K to 300K");
}); });
