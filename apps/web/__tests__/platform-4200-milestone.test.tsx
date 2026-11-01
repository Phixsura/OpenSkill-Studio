import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Platform4200Milestone } from "@/components/platform-4200-milestone";
describe("Platform4200Milestone", () => { it("renders", () => {
    const { container } = render(<Platform4200Milestone />);
    expect(container.textContent).toContain("4,200");
    expect(container.textContent).toContain("NEVER. STOP. BUILDING.");
}); });
