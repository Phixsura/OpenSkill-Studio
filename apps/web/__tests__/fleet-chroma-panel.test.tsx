import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetChromaPanel } from "@/components/fleet-chroma-panel";
describe("FleetChromaPanel", () => { it("renders", () => {
    const { container } = render(<FleetChromaPanel collections={5} documents={500000} embeddings={500000} synced={true} />);
    expect(container.textContent).toContain("Chroma");
    expect(container.textContent).toContain("500,000 docs");
}); });
