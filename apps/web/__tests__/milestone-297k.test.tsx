import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone297k } from "@/components/milestone-297k";
describe("Milestone297k", () => { it("renders", () => {
    const { container } = render(<Milestone297k />);
    expect(container.textContent).toContain("297K");
    expect(container.textContent).toContain("300K");
}); });
