import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV11018kPanel } from "@/components/platform-v110-18k-panel";
describe("PlatformV11018kPanel", () => { it("renders", () => {
    const { container } = render(<PlatformV11018kPanel />);
    expect(container.textContent).toContain("v110");
    expect(container.textContent).toContain("18K");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
