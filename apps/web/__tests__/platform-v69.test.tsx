import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV69 } from "@/components/platform-v69";
describe("PlatformV69", () => { it("renders", () => {
    const { container } = render(<PlatformV69 />);
    expect(container.textContent).toContain("v69");
}); });
