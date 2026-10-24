import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone318kImminent } from "@/components/milestone-318k-imminent";
describe("Milestone318kImminent", () => { it("renders", () => {
    const { container } = render(<Milestone318kImminent />);
    expect(container.textContent).toContain("318K");
}); });
