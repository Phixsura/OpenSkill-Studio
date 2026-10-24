import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone299k } from "@/components/milestone-299k";
describe("Milestone299k", () => { it("renders", () => {
    const { container } = render(<Milestone299k />);
    expect(container.textContent).toContain("299K");
    expect(container.textContent).toContain("ONE THOUSAND");
}); });
