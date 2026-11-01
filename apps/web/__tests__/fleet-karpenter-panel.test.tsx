import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetKarpenterPanel } from "@/components/fleet-karpenter-panel";
describe("FleetKarpenterPanel", () => { it("renders", () => {
    const { container } = render(<FleetKarpenterPanel provisioners={3} active={3} launched={15} terminated={12} savings={750} />);
    expect(container.textContent).toContain("Karpenter");
    expect(container.textContent).toContain("$750 saved");
}); });
