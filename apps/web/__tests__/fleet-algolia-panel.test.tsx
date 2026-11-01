import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAlgoliaPanel } from "@/components/fleet-algolia-panel";
describe("FleetAlgoliaPanel", () => { it("renders", () => {
    const { container } = render(<FleetAlgoliaPanel indices={20} records={50000000} operations={200000000} avgLatency={4} />);
    expect(container.textContent).toContain("Algolia");
}); });
