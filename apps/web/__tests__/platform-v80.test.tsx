import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV80 } from "@/components/platform-v80";
describe("PlatformV80", () => { it("renders", () => {
    const { container } = render(<PlatformV80 />);
    expect(container.textContent).toContain("v80");
    expect(container.textContent).toContain("BIG 80");
}); });
