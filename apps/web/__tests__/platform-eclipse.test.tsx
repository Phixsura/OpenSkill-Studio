import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformEclipse } from "@/components/platform-eclipse";
describe("PlatformEclipse", () => { it("renders", () => {
    const { container } = render(<PlatformEclipse />);
    expect(container.textContent).toContain("ECLIPSE");
    expect(container.textContent).toContain("PERMANENT");
}); });
