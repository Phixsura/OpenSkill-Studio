import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone314k } from "@/components/milestone-314k";
describe("Milestone314k", () => { it("renders", () => {
    const { container } = render(<Milestone314k />);
    expect(container.textContent).toContain("314K");
}); });
