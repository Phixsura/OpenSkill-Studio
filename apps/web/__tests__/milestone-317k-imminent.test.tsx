import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone317kImminent } from "@/components/milestone-317k-imminent";
describe("Milestone317kImminent", () => { it("renders", () => {
    const { container } = render(<Milestone317kImminent />);
    expect(container.textContent).toContain("317K");
}); });
