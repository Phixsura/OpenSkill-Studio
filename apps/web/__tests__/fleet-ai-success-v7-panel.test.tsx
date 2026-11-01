import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSuccessV7Panel } from "@/components/fleet-ai-success-v7-panel";
describe("FleetAiSuccessV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiSuccessV7Panel trackers={3} active={3} health={95} churnRisk={3} expansion={200000000} />);
    expect(container.textContent).toContain("Success v7");
}); });
