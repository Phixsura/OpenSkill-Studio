import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthV5Panel } from "@/components/fleet-ai-health-v5-panel";
describe("FleetAiHealthV5Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthV5Panel checkers={5} active={5} services={5000} healthy={5000} score={100} uptime={99.9999} />);
    expect(container.textContent).toContain("Health v5");
}); });
