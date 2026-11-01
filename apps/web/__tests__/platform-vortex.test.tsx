import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformVortex } from "@/components/platform-vortex";
describe("PlatformVortex", () => { it("renders", () => {
    const { container } = render(<PlatformVortex />);
    expect(container.textContent).toContain("VORTEX");
    expect(container.textContent).toContain("IRRESISTIBLE");
}); });
