import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetFeastPanel } from "@/components/fleet-feast-panel";
describe("FleetFeastPanel", () => { it("renders", () => {
    const { container } = render(<FleetFeastPanel projects={5} active={5} featureViews={100} entities={40} />);
    expect(container.textContent).toContain("Feast");
}); });
