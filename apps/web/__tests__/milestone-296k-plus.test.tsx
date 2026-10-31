import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone296kPlus } from "@/components/milestone-296k-plus";
describe("Milestone296kPlus", () => { it("renders", () => {
    const { container } = render(<Milestone296kPlus />);
    expect(container.textContent).toContain("296K+");
}); });
