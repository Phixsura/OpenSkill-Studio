import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCrdPanel } from "@/components/fleet-crd-panel";
describe("FleetCrdPanel", () => { it("renders", () => {
    const { container } = render(<FleetCrdPanel total={15} healthy={13} stale={2} allEstablished={false} />);
    expect(container.textContent).toContain("CRDs");
    expect(container.textContent).toContain("Not all CRDs");
}); });
