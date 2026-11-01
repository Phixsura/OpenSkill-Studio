import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformEmpyrean } from "@/components/platform-empyrean";
describe("PlatformEmpyrean", () => { it("renders", () => {
    const { container } = render(<PlatformEmpyrean />);
    expect(container.textContent).toContain("EMPYREAN");
    expect(container.textContent).toContain("Seraphim");
}); });
