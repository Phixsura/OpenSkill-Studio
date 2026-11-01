import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEmbeddingsPanel } from "@/components/fleet-ai-embeddings-panel";
describe("FleetAiEmbeddingsPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEmbeddingsPanel pipelines={5} active={5} vectors={10000000} dims={1536} />);
    expect(container.textContent).toContain("AI Embeddings");
}); });
