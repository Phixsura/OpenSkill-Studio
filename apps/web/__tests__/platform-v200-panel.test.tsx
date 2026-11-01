import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV200Panel } from "@/components/platform-v200-panel";
describe("PlatformV200Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV200Panel />);
    expect(container.textContent).toContain("v200");
    expect(container.textContent).toContain("TWO HUNDRED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
