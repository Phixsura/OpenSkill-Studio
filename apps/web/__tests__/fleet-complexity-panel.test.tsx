import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetComplexityPanel } from "@/components/fleet-complexity-panel";
describe("FleetComplexityPanel", () => { it("renders", () => {
    const { container } = render(<FleetComplexityPanel modules={50} avgComplexity={12} highComplexity={5} maintainable={true} />);
    expect(container.textContent).toContain("Complexity");
    expect(container.textContent).toContain("avg 12");
}); });
