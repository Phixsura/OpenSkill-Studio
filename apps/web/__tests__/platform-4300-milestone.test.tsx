import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Platform4300Milestone } from "@/components/platform-4300-milestone";
describe("Platform4300Milestone", () => { it("renders", () => {
    const { container } = render(<Platform4300Milestone />);
    expect(container.textContent).toContain("4,300");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
