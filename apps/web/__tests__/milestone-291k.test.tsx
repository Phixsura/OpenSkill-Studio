import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone291k } from "@/components/milestone-291k";
describe("Milestone291k", () => { it("renders", () => {
    const { container } = render(<Milestone291k />);
    expect(container.textContent).toContain("291,000");
}); });
