import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV90Panel } from "@/components/platform-v90-panel";
describe("PlatformV90Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV90Panel />);
    expect(container.textContent).toContain("v90");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
