import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatChlogV2Panel } from "@/components/fleet-ai-plat-chlog-v2-panel";
describe("FleetAiPlatChlogV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatChlogV2Panel logs={2} active={2} releases={500} features={2000} fixes={1000} subscribers={200000} />);
    expect(container.textContent).toContain("Changelog v2");
}); });
