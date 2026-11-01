import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone293k } from "@/components/milestone-293k";
describe("Milestone293k", () => { it("renders", () => {
    const { container } = render(<Milestone293k />);
    expect(container.textContent).toContain("293K");
}); });
