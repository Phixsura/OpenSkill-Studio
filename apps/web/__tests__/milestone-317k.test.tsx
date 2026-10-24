import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone317k } from "@/components/milestone-317k";
describe("Milestone317k", () => { it("renders", () => {
    const { container } = render(<Milestone317k />);
    expect(container.textContent).toContain("317K");
}); });
