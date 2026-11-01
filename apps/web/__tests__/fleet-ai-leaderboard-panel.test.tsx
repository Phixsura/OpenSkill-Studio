import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiLeaderboardPanel } from "@/components/fleet-ai-leaderboard-panel";
describe("FleetAiLeaderboardPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiLeaderboardPanel boards={3} active={3} models={500} benchmarks={100} submissions={5000} />);
    expect(container.textContent).toContain("AI Leaderboard");
}); });
