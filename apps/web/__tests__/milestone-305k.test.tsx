import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone305k } from "@/components/milestone-305k";
describe("Milestone305k", () => { it("renders", () => {
    const { container } = render(<Milestone305k />);
    expect(container.textContent).toContain("305K");
}); });
