import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiApiEconomyV7Panel } from "@/components/fleet-ai-api-economy-v7-panel";
describe("FleetAiApiEconomyV7Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiApiEconomyV7Panel trackers={3} active={3} apis={2000} revenue={500000000} developers={2000000} calls={200000000000} />);
    expect(container.textContent).toContain("API Economy v7");
}); });
