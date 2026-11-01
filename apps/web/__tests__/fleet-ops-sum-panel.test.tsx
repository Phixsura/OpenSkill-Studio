import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpsSumPanel } from "@/components/fleet-ops-sum-panel";
describe("FleetOpsSumPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpsSumPanel incidentsOpen={0} deploysToday={10} alertsFiring={0} status="calm" />);
    expect(container.textContent).toContain("Ops Summary");
    expect(container.textContent).toContain("CALM");
}); });
