import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCbV2Panel } from "@/components/fleet-ai-cb-v2-panel";
describe("FleetAiCbV2Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCbV2Panel breakers={10} active={10} closed={10} halfOpen={0} open={0} trips={5} />);
    expect(container.textContent).toContain("Circuit Breaker v2");
}); });
