import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone3397290k } from "@/components/milestone-3397-290k";
describe("Milestone3397290k", () => { it("renders", () => {
    const { container } = render(<Milestone3397290k />);
    expect(container.textContent).toContain("3,397 Commits");
}); });
