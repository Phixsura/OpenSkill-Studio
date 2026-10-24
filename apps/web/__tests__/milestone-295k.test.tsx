import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone295k } from "@/components/milestone-295k";
describe("Milestone295k", () => { it("renders", () => {
    const { container } = render(<Milestone295k />);
    expect(container.textContent).toContain("295K");
}); });
