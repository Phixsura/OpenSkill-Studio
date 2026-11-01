import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetGameDayPanel } from "@/components/fleet-game-day-panel";
describe("FleetGameDayPanel", () => { it("renders", () => {
    const { container } = render(<FleetGameDayPanel total={5} passed={3} failed={2} learnings={10} resilient={false} />);
    expect(container.textContent).toContain("Game Day");
    expect(container.textContent).toContain("Weaknesses found");
}); });
