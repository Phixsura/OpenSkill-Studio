import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAi3dGenPanel } from "@/components/fleet-ai-3d-gen-panel";
describe("FleetAi3dGenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAi3dGenPanel generators={3} active={3} models={200000} avgPolys={250000} textured={3} />);
    expect(container.textContent).toContain("3D Generation");
}); });
