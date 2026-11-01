import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDspyPanel } from "@/components/fleet-dspy-panel";
describe("FleetDspyPanel", () => { it("renders", () => {
    const { container } = render(<FleetDspyPanel programs={10} deployed={10} modules={50} optimizations={2000} />);
    expect(container.textContent).toContain("DSPy");
}); });
