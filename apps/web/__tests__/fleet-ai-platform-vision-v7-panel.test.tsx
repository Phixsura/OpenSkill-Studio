import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatformVisionV7Panel } from "@/components/fleet-ai-platform-vision-v7-panel";
describe("FleetAiPlatformVisionV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatformVisionV7Panel planners={3} active={3} goals={100} achieved={80} horizon={10} />);
    expect(container.textContent).toContain("Platform Vision v7");
}); });
