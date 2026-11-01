import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatQualV2Panel } from "@/components/fleet-ai-plat-qual-v2-panel";
describe("FleetAiPlatQualV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatQualV2Panel monitors={4} active={4} coverage={95} bugs={5} debt={50} />);
    expect(container.textContent).toContain("Quality v2");
}); });
