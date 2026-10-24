import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3490 } from "@/components/milestone-3490";
describe("Milestone3490", () => { it("renders", () => {
    const { container } = render(<Milestone3490 />);
    expect(container.textContent).toContain("3,490");
}); });
