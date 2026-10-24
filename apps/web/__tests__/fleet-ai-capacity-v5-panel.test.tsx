import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiCapacityV5Panel } from "@/components/fleet-ai-capacity-v5-panel";
describe("FleetAiCapacityV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiCapacityV5Panel planners={3} active={3} gpus={100000} headroom={40} forecast={730} />);
    expect(container.textContent).toContain("Capacity v5");
}); });
