import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetWeaviatePanel } from "@/components/fleet-weaviate-panel";
describe("FleetWeaviatePanel", () => { it("renders", () => {
    const { container } = render(<FleetWeaviatePanel nodes={3} healthy={3} objects={1500000} vectors={1500000} />);
    expect(container.textContent).toContain("Weaviate");
    expect(container.textContent).toContain("1,500,000 objects");
}); });
