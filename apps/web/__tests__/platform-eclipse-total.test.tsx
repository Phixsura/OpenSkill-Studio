import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformEclipseTotal } from "@/components/platform-eclipse-total";
describe("PlatformEclipseTotal", () => { it("renders", () => {
    const { container } = render(<PlatformEclipseTotal />);
    expect(container.textContent).toContain("ECLIPSE TOTAL");
    expect(container.textContent).toContain("pytest");
}); });
