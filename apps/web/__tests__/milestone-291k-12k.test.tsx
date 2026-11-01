import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone291k12k } from "@/components/milestone-291k-12k";
describe("Milestone291k12k", () => { it("renders", () => {
    const { container } = render(<Milestone291k12k />);
    expect(container.textContent).toContain("291K+");
    expect(container.textContent).toContain("12K");
}); });
