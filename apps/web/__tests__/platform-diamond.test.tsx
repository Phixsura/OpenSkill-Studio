import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformDiamond } from "@/components/platform-diamond";
describe("PlatformDiamond", () => { it("renders", () => {
    const { container } = render(<PlatformDiamond />);
    expect(container.textContent).toContain("DIAMOND");
    expect(container.textContent).toContain("FLAWLESS");
}); });
