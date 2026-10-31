import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone301k } from "@/components/milestone-301k";
describe("Milestone301k", () => { it("renders", () => {
    const { container } = render(<Milestone301k />);
    expect(container.textContent).toContain("301K");
}); });
