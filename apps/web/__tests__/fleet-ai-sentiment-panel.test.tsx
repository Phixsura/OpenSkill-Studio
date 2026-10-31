import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSentimentPanel } from "@/components/fleet-ai-sentiment-panel";
describe("FleetAiSentimentPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSentimentPanel analyzers={3} active={3} analyzed={20000000} accuracy={96} emotions={8} />);
    expect(container.textContent).toContain("Sentiment");
}); });
