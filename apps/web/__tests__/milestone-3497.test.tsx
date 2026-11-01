import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3497 } from "@/components/milestone-3497";
describe("Milestone3497", () => { it("renders", () => {
    const { container } = render(<Milestone3497 />);
    expect(container.textContent).toContain("3,497");
    expect(container.textContent).toContain("3,500");
}); });
