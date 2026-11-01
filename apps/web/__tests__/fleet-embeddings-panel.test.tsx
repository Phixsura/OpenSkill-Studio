import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetEmbeddingsPanel } from "@/components/fleet-embeddings-panel";
describe("FleetEmbeddingsPanel", () => { it("renders", () => {
    const { container } = render(<FleetEmbeddingsPanel services={5} active={5} embeddings={50000000} maxDimensions={3072} />);
    expect(container.textContent).toContain("Embeddings");
}); });
