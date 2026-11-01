import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone296k } from "@/components/milestone-296k";
describe("Milestone296k", () => { it("renders", () => {
    const { container } = render(<Milestone296k />);
    expect(container.textContent).toContain("296K");
    expect(container.textContent).toContain("300K");
}); });
