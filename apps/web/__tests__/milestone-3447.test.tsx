import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3447 } from "@/components/milestone-3447";
describe("Milestone3447", () => { it("renders", () => {
    const { container } = render(<Milestone3447 />);
    expect(container.textContent).toContain("3,447");
}); });
