import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiVisionV8Panel } from "@/components/fleet-ai-vision-v8-panel";
describe("FleetAiVisionV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiVisionV8Panel planners={3} active={3} goals={200} achieved={160} horizon={15} />);
    expect(container.textContent).toContain("Vision v8");
}); });
