import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3450 } from "@/components/milestone-3450";
describe("Milestone3450", () => { it("renders", () => {
    const { container } = render(<Milestone3450 />);
    expect(container.textContent).toContain("3,450");
    expect(container.textContent).toContain("IMMINENT");
}); });
