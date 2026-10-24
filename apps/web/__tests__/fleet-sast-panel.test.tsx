import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSastPanel } from "@/components/fleet-sast-panel";
describe("FleetSastPanel", () => { it("renders", () => {
    const { container } = render(<FleetSastPanel scans={10} totalFindings={15} critical={1} high={2} secure={false} />);
    expect(container.textContent).toContain("SAST Results");
    expect(container.textContent).toContain("1 critical");
}); });
