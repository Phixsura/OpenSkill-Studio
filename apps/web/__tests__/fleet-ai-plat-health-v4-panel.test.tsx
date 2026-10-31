import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatHealthV4Panel } from "@/components/fleet-ai-plat-health-v4-panel";
describe("FleetAiPlatHealthV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatHealthV4Panel checkers={5} active={5} services={5000} healthy={5000} uptime={99.999} score={100} />);
    expect(container.textContent).toContain("Platform Health v4");
}); });
