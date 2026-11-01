import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiHealthV8Panel } from "@/components/fleet-ai-health-v8-panel";
describe("FleetAiHealthV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiHealthV8Panel checkers={5} active={5} services={20000} healthy={20000} score={100} uptime={99.9999} />);
    expect(container.textContent).toContain("Health v8");
}); });
