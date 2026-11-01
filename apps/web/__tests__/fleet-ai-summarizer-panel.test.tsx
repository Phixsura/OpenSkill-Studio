import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSummarizerPanel } from "@/components/fleet-ai-summarizer-panel";
describe("FleetAiSummarizerPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSummarizerPanel services={5} active={5} docs={500000} avgCompression={5} />);
    expect(container.textContent).toContain("AI Summarizer");
}); });
