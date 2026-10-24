import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV150Panel } from "@/components/platform-v150-panel";
describe("PlatformV150Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV150Panel />);
    expect(container.textContent).toContain("v150");
    expect(container.textContent).toContain("150");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
