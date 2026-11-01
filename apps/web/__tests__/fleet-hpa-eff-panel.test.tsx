import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHpaEffPanel } from "@/components/fleet-hpa-eff-panel";
describe("FleetHpaEffPanel", () => { it("renders", () => {
    const { container } = render(<FleetHpaEffPanel total={5} responsive={3} avgScaleTime={120} effective={false} />);
    expect(container.textContent).toContain("HPA Effectiveness");
    expect(container.textContent).toContain("Slow autoscaling");
}); });
