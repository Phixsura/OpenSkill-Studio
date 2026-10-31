import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatIncV3Panel } from "@/components/fleet-ai-plat-inc-v3-panel";
describe("FleetAiPlatIncV3Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatIncV3Panel managers={3} active={3} incidents={20} p1={3} mttr={8} postmortems={3} />);
    expect(container.textContent).toContain("Incident v3");
}); });
