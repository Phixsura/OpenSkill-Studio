import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSearchPanel } from "@/components/fleet-ai-search-panel";
describe("FleetAiSearchPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSearchPanel engines={5} active={5} queries={25000000} relevance={94} />);
    expect(container.textContent).toContain("AI Search");
}); });
