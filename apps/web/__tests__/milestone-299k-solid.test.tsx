import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone299kSolid } from "@/components/milestone-299k-solid";
describe("Milestone299kSolid", () => { it("renders", () => {
    const { container } = render(<Milestone299kSolid />);
    expect(container.textContent).toContain("299K+");
    expect(container.textContent).toContain("1,400");
}); });
