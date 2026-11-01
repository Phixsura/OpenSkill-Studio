import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformForge } from "@/components/platform-forge";
describe("PlatformForge", () => { it("renders", () => {
    const { container } = render(<PlatformForge />);
    expect(container.textContent).toContain("FORGE");
    expect(container.textContent).toContain("Damascus");
}); });
