import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone317k3650 } from "@/components/milestone-317k-3650";
describe("Milestone317k3650", () => { it("renders", () => {
    const { container } = render(<Milestone317k3650 />);
    expect(container.textContent).toContain("317K+");
    expect(container.textContent).toContain("3,650");
}); });
