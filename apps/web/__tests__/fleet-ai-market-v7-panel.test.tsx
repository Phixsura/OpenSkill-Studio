import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiMarketV7Panel } from "@/components/fleet-ai-market-v7-panel";
describe("FleetAiMarketV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiMarketV7Panel trackers={2} active={2} share={40} tam={100000000000} competitors={30} winRate={75} />);
    expect(container.textContent).toContain("Market v7");
}); });
