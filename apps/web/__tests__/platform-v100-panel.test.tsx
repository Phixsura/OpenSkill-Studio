import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV100Panel } from "@/components/platform-v100-panel";
describe("PlatformV100Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV100Panel />);
    expect(container.textContent).toContain("v100");
    expect(container.textContent).toContain("ONE HUNDRED");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
