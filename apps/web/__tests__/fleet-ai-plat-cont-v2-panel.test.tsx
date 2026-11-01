import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatContV2Panel } from "@/components/fleet-ai-plat-cont-v2-panel";
describe("FleetAiPlatContV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatContV2Panel runtimes={5} active={5} containers={10000} images={1000} registries={20} />);
    expect(container.textContent).toContain("AI Container v2");
}); });
