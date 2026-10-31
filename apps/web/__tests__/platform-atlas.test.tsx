import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformAtlas } from "@/components/platform-atlas";
describe("PlatformAtlas", () => { it("renders", () => {
    const { container } = render(<PlatformAtlas />);
    expect(container.textContent).toContain("ATLAS");
    expect(container.textContent).toContain("Backend");
    expect(container.textContent).toContain("Unexplored: 0");
}); });
