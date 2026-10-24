import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone315kImminent } from "@/components/milestone-315k-imminent";
describe("Milestone315kImminent", () => { it("renders", () => {
    const { container } = render(<Milestone315kImminent />);
    expect(container.textContent).toContain("315K");
}); });
