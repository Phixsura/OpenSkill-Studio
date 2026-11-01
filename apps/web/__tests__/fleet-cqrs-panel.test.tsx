import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCqrsPanel } from "@/components/fleet-cqrs-panel";
describe("FleetCqrsPanel", () => { it("renders", () => {
    const { container } = render(<FleetCqrsPanel total={20} cqrsEnabled={10} readReplicas={15} adoptionPct={50} />);
    expect(container.textContent).toContain("CQRS");
    expect(container.textContent).toContain("50%");
}); });
