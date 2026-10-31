import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiRerankerPanel } from "@/components/fleet-ai-reranker-panel";
describe("FleetAiRerankerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiRerankerPanel rerankers={3} active={3} queries={20000000} ndcgBoost={0.2} latency={15} />);
    expect(container.textContent).toContain("AI Reranker");
}); });
