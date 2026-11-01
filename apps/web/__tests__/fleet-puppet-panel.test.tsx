import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPuppetPanel } from "@/components/fleet-puppet-panel";
describe("FleetPuppetPanel", () => { it("renders", () => {
    const { container } = render(<FleetPuppetPanel total={100} inSync={90} changed={5} failed={5} />);
    expect(container.textContent).toContain("Puppet");
    expect(container.textContent).toContain("5 failed");
}); });
