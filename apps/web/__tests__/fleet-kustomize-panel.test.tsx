import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKustomizePanel } from "@/components/fleet-kustomize-panel";
describe("FleetKustomizePanel", () => { it("renders", () => {
    const { container } = render(<FleetKustomizePanel total={15} valid={13} invalid={2} stale={1} clean={false} />);
    expect(container.textContent).toContain("Kustomize");
    expect(container.textContent).toContain("2 invalid");
}); });
