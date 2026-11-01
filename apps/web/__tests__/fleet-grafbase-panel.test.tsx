import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGrafbasePanel } from "@/components/fleet-grafbase-panel";
describe("FleetGrafbasePanel", () => { it("renders", () => {
    const { container } = render(<FleetGrafbasePanel projects={5} deployed={5} resolvers={200} requests={10000000} />);
    expect(container.textContent).toContain("Grafbase");
}); });
