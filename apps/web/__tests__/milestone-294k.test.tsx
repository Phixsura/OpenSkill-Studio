import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone294k } from "@/components/milestone-294k";
describe("Milestone294k", () => { it("renders", () => {
    const { container } = render(<Milestone294k />);
    expect(container.textContent).toContain("294K");
}); });
