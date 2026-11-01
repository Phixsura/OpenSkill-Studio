import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone323kImminent } from "@/components/milestone-323k-imminent";
describe("Milestone323kImminent", () => { it("renders", () => {
    const { container } = render(<Milestone323kImminent />);
    expect(container.textContent).toContain("323K");
}); });
