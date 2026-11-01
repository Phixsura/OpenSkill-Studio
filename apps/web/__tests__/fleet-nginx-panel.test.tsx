import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetNginxPanel } from "@/components/fleet-nginx-panel";
describe("FleetNginxPanel", () => { it("renders", () => {
    const { container } = render(<FleetNginxPanel controllers={3} activeConns={15000} rps={30000} errors5xx={10} healthy={false} />);
    expect(container.textContent).toContain("NGINX");
    expect(container.textContent).toContain("10 5xx");
}); });
