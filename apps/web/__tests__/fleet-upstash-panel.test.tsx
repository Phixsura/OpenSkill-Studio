import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetUpstashPanel } from "@/components/fleet-upstash-panel";
describe("FleetUpstashPanel", () => { it("renders", () => {
    const { container } = render(<FleetUpstashPanel databases={5} active={5} commands={50000000} bandwidthGb={25} />);
    expect(container.textContent).toContain("Upstash");
    expect(container.textContent).toContain("50,000,000");
}); });
