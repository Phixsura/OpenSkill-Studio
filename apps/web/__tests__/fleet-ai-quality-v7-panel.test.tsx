import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiQualityV7Panel } from "@/components/fleet-ai-quality-v7-panel";
describe("FleetAiQualityV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiQualityV7Panel monitors={4} active={4} coverage={98} debt={50} bugs={2} smells={10} />);
    expect(container.textContent).toContain("Quality v7");
}); });
