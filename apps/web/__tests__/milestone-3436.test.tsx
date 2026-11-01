import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3436 } from "@/components/milestone-3436";
describe("Milestone3436", () => { it("renders", () => {
    const { container } = render(<Milestone3436 />);
    expect(container.textContent).toContain("3,436");
    expect(container.textContent).toContain("COUNTDOWN");
}); });
