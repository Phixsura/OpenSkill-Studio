import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3360Panel } from "@/components/milestone-3360-panel";
describe("Milestone3360Panel", () => { it("renders", () => {
    const { container } = render(<Milestone3360Panel />);
    expect(container.textContent).toContain("3,360 Commits");
}); });
