import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV600Panel } from "@/components/platform-v600-panel";
describe("PlatformV600Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV600Panel />);
    expect(container.textContent).toContain("v600");
    expect(container.textContent).toContain("SIX HUNDRED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
