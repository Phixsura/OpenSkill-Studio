import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatDrV2Panel } from "@/components/fleet-ai-plat-dr-v2-panel";
describe("FleetAiPlatDrV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatDrV2Panel plans={3} active={3} rto={3} rpo={1} drills={8} regions={10} />);
    expect(container.textContent).toContain("AI DR v2");
}); });
