import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3460 } from "@/components/milestone-3460";
describe("Milestone3460", () => { it("renders", () => {
    const { container } = render(<Milestone3460 />);
    expect(container.textContent).toContain("3,460");
}); });
