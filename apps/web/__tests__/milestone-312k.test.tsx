import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone312k } from "@/components/milestone-312k";
describe("Milestone312k", () => { it("renders", () => {
    const { container } = render(<Milestone312k />);
    expect(container.textContent).toContain("312K");
}); });
