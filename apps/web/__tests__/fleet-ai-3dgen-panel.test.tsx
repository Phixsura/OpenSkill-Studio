import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAi3dgenPanel } from "@/components/fleet-ai-3dgen-panel";
describe("FleetAi3dgenPanel", () => { it("renders", () => {
    const { container } = render(<FleetAi3dgenPanel services={3} active={3} models={30000} vertices={1500000000} />);
    expect(container.textContent).toContain("AI 3D Gen");
}); });
