import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV300Panel } from "@/components/platform-v300-panel";
describe("PlatformV300Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV300Panel />);
    expect(container.textContent).toContain("v300");
    expect(container.textContent).toContain("THREE HUNDRED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
