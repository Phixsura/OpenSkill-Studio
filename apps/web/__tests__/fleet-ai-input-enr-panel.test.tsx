import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiInputEnrPanel } from "@/components/fleet-ai-input-enr-panel";
describe("FleetAiInputEnrPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiInputEnrPanel enrichers={4} active={4} enriched={20000000} sources={30} addedTokens={800} />);
    expect(container.textContent).toContain("Input Enricher");
}); });
