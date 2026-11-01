import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3508 } from "@/components/milestone-3508";
describe("Milestone3508", () => { it("renders", () => {
    const { container } = render(<Milestone3508 />);
    expect(container.textContent).toContain("3,508");
}); });
