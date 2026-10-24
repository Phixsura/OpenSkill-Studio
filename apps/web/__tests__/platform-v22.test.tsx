import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV22 } from "@/components/platform-v22";
describe("PlatformV22", () => { it("renders", () => {
    const { container } = render(<PlatformV22 />);
    expect(container.textContent).toContain("v22.0");
    expect(container.textContent).toContain("ULTIMATE");
}); });
