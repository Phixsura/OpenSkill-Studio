import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Milestone303k } from "@/components/milestone-303k";
describe("Milestone303k", () => { it("renders", () => {
    const { container } = render(<Milestone303k />);
    expect(container.textContent).toContain("303K");
}); });
