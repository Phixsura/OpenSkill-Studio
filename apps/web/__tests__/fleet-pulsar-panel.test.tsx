import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPulsarPanel } from "@/components/fleet-pulsar-panel";
describe("FleetPulsarPanel", () => { it("renders", () => {
    const { container } = render(<FleetPulsarPanel clusters={3} healthy={3} topics={3000} msgPerSec={300000} />);
    expect(container.textContent).toContain("Pulsar");
}); });
