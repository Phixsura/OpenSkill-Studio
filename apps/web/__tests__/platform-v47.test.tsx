import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV47 } from "@/components/platform-v47";
describe("PlatformV47", () => { it("renders", () => {
    const { container } = render(<PlatformV47 />);
    expect(container.textContent).toContain("v47");
    expect(container.textContent).toContain("16K");
}); });
