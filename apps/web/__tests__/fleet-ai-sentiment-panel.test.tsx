import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiSentimentPanel } from "@/components/fleet-ai-sentiment-panel";
describe("FleetAiSentimentPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiSentimentPanel services={5} active={5} analyses={15000000} positivePct={75} />);
    expect(container.textContent).toContain("AI Sentiment");
}); });
