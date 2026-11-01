import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3600Hit } from "@/components/milestone-3600-hit";
describe("Milestone3600Hit", () => { it("renders", () => {
    const { container } = render(<Milestone3600Hit />);
    expect(container.textContent).toContain("3,600 COMMITS");
}); });
