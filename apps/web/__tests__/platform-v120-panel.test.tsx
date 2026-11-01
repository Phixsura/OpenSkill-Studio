import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV120Panel } from "@/components/platform-v120-panel";
describe("PlatformV120Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV120Panel />);
    expect(container.textContent).toContain("v120");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
