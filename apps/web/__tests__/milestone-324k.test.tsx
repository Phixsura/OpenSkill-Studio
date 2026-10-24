import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone324k } from "@/components/milestone-324k";
describe("Milestone324k", () => { it("renders", () => {
    const { container } = render(<Milestone324k />);
    expect(container.textContent).toContain("324K");
}); });
