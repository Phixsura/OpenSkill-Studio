import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEmbIndexPanel } from "@/components/fleet-ai-emb-index-panel";
describe("FleetAiEmbIndexPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEmbIndexPanel indexes={5} active={5} vectors={500000000} dims={3072} searches={50000000} p99={10} />);
    expect(container.textContent).toContain("Embedding Index");
}); });
