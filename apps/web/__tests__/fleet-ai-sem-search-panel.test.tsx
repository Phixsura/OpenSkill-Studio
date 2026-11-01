import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSemSearchPanel } from "@/components/fleet-ai-sem-search-panel";
describe("FleetAiSemSearchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSemSearchPanel engines={4} active={4} queries={10000000} docs={500000000} mrr={0.95} />);
    expect(container.textContent).toContain("Semantic Search");
}); });
