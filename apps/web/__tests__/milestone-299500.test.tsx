import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone299500 } from "@/components/milestone-299500";
describe("Milestone299500", () => { it("renders", () => {
    const { container } = render(<Milestone299500 />);
    expect(container.textContent).toContain("299,500");
    expect(container.textContent).toContain("UNDER 1,000");
}); });
