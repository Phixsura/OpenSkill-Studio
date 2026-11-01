import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiEmbIdxPanel } from "@/components/fleet-ai-emb-idx-panel";
describe("FleetAiEmbIdxPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiEmbIdxPanel indexes={5} active={5} vectors={500000000} searches={50000000} avgMs={8} />);
    expect(container.textContent).toContain("Embedding Index");
}); });
