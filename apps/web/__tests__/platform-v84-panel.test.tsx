import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV84Panel } from "@/components/platform-v84-panel";
describe("PlatformV84Panel", () => { it("renders", () => {
    const { container } = render(<PlatformV84Panel />);
    expect(container.textContent).toContain("v84");
}); });
