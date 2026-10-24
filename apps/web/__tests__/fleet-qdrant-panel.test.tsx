import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetQdrantPanel } from "@/components/fleet-qdrant-panel";
describe("FleetQdrantPanel", () => { it("renders", () => {
    const { container } = render(<FleetQdrantPanel collections={10} green={10} totalPoints={50000000} />);
    expect(container.textContent).toContain("Qdrant");
    expect(container.textContent).toContain("50,000,000");
}); });
