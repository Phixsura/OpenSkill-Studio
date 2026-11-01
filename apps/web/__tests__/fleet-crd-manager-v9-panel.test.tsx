import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCrdManagerV9Panel } from "@/components/fleet-crd-manager-v9-panel";
describe("FleetCrdManagerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCrdManagerV9Panel crds={20} instances={500} />);
    expect(container.textContent).toContain("CRD Manager v9");
}); });
