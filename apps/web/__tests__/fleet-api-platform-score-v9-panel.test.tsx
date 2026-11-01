import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPlatformScoreV9Panel } from "@/components/fleet-api-platform-score-v9-panel";
describe("FleetApiPlatformScoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPlatformScoreV9Panel />);
    expect(container.textContent).toContain("A+");
    expect(container.textContent).toContain("NEVER STOPS");
}); });
