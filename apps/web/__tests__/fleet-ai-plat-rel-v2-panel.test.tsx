import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatRelV2Panel } from "@/components/fleet-ai-plat-rel-v2-panel";
describe("FleetAiPlatRelV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatRelV2Panel systems={5} active={5} uptime={99.999} incidents={3} mttr={5} budget={80} />);
    expect(container.textContent).toContain("Reliability v2");
}); });
