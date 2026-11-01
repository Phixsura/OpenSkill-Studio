import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone323k } from "@/components/milestone-323k";
describe("Milestone323k", () => { it("renders", () => {
    const { container } = render(<Milestone323k />);
    expect(container.textContent).toContain("323K");
}); });
