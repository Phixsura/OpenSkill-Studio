import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformSolaris } from "@/components/platform-solaris";
describe("PlatformSolaris", () => { it("renders", () => {
    const { container } = render(<PlatformSolaris />);
    expect(container.textContent).toContain("SOLARIS");
    expect(container.textContent).toContain("Marketplace");
}); });
