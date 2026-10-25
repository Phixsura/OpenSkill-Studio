import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformTidalForce } from "@/components/platform-tidal-force";
describe("PlatformTidalForce", () => { it("renders", () => {
    const { container } = render(<PlatformTidalForce />);
    expect(container.textContent).toContain("TIDAL FORCE");
    expect(container.textContent).toContain("ZERO");
}); });
