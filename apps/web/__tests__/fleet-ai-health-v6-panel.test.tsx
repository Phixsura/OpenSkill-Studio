import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthV6Panel } from "@/components/fleet-ai-health-v6-panel";
describe("FleetAiHealthV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthV6Panel checkers={5} active={5} services={10000} healthy={10000} uptime={99.9999} />);
    expect(container.textContent).toContain("Health v6");
}); });
