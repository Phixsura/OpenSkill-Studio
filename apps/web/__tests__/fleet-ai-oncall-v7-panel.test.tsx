import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiOncallV7Panel } from "@/components/fleet-ai-oncall-v7-panel";
describe("FleetAiOncallV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiOncallV7Panel schedulers={4} active={4} engineers={80} pages={30} ack={0.5} auto={25} />);
    expect(container.textContent).toContain("On-Call v7");
}); });
