import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiChunkerPanel } from "@/components/fleet-ai-chunker-panel";
describe("FleetAiChunkerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiChunkerPanel chunkers={4} active={4} docs={5000000} chunks={200000000} avgTokens={256} />);
    expect(container.textContent).toContain("AI Chunker");
}); });
