import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV24 } from "@/components/platform-v24";
describe("PlatformV24", () => { it("renders", () => {
    const { container } = render(<PlatformV24 />);
    expect(container.textContent).toContain("v24.0");
    expect(container.textContent).toContain("3,600");
}); });
