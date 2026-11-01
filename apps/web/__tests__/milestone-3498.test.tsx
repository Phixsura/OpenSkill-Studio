import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3498 } from "@/components/milestone-3498";
describe("Milestone3498", () => { it("renders", () => {
    const { container } = render(<Milestone3498 />);
    expect(container.textContent).toContain("3,498");
    expect(container.textContent).toContain("3,500");
}); });
