import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOpentofuPanel } from "@/components/fleet-opentofu-panel";
describe("FleetOpentofuPanel", () => { it("renders", () => {
    const { container } = render(<FleetOpentofuPanel total={10} clean={8} withChanges={2} totalResources={200} />);
    expect(container.textContent).toContain("OpenTofu");
    expect(container.textContent).toContain("2 pending");
}); });
