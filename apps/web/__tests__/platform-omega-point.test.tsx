import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformOmegaPoint } from "@/components/platform-omega-point";
describe("PlatformOmegaPoint", () => { it("renders", () => {
    const { container } = render(<PlatformOmegaPoint />);
    expect(container.textContent).toContain("OMEGA POINT");
    expect(container.textContent).toContain("always more");
}); });
