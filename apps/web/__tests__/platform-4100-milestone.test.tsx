import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { Platform4100Milestone } from "@/components/platform-4100-milestone";
describe("Platform4100Milestone", () => { it("renders", () => {
    const { container } = render(<Platform4100Milestone />);
    expect(container.textContent).toContain("4,100");
    expect(container.textContent).toContain("Never stop");
}); });
