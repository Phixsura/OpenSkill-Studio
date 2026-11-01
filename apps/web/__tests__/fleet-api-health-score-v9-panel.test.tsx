import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiHealthScoreV9Panel } from "@/components/fleet-api-health-score-v9-panel";
describe("FleetApiHealthScoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiHealthScoreV9Panel endpoints={200} score={97} />);
    expect(container.textContent).toContain("API Health Score v9");
}); });
