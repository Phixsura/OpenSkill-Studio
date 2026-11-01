import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMonV6Panel } from "@/components/fleet-ai-mon-v6-panel";
describe("FleetAiMonV6Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMonV6Panel monitors={5} active={5} services={10000} metrics={1000000} uptime={99.9999} />);
    expect(container.textContent).toContain("Monitoring v6");
}); });
