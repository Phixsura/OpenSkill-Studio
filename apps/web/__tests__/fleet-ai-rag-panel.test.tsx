import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRagPanel } from "@/components/fleet-ai-rag-panel";
describe("FleetAiRagPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRagPanel pipelines={5} active={5} queries={2000000} docs={50000000} relevance={0.92} />);
    expect(container.textContent).toContain("RAG Pipeline");
}); });
