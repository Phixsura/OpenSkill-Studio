import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSummarizePanel } from "@/components/fleet-ai-summarize-panel";
describe("FleetAiSummarizePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSummarizePanel services={4} active={4} docs={2000000} compression={10} rougeL={0.88} />);
    expect(container.textContent).toContain("Summarization");
}); });
