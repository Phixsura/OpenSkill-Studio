import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDoraGradePanel } from "@/components/fleet-dora-grade-panel";
describe("FleetDoraGradePanel", () => { it("renders", () => {
    const { container } = render(<FleetDoraGradePanel overall="Elite" score={3.75} df="Elite" lt="Elite" cfr="Elite" mttr="High" />);
    expect(container.textContent).toContain("DORA Overall");
    expect(container.textContent).toContain("Elite");
}); });
