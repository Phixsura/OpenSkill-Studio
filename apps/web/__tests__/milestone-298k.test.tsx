import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone298k } from "@/components/milestone-298k";
describe("Milestone298k", () => { it("renders", () => {
    const { container } = render(<Milestone298k />);
    expect(container.textContent).toContain("298K");
    expect(container.textContent).toContain("TWO THOUSAND");
}); });
