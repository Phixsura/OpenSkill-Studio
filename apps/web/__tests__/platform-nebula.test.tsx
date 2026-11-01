import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformNebula } from "@/components/platform-nebula";
describe("PlatformNebula", () => { it("renders", () => {
    const { container } = render(<PlatformNebula />);
    expect(container.textContent).toContain("NEBULA");
    expect(container.textContent).toContain("Hydrogen");
}); });
