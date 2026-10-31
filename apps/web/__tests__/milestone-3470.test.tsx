import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3470 } from "@/components/milestone-3470";
describe("Milestone3470", () => { it("renders", () => {
    const { container } = render(<Milestone3470 />);
    expect(container.textContent).toContain("3,470");
}); });
