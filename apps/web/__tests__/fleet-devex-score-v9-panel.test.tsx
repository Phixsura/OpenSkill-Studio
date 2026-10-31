import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDevexScoreV9Panel } from "@/components/fleet-devex-score-v9-panel";
describe("FleetDevexScoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDevexScoreV9Panel teams={15} score={92} />);
    expect(container.textContent).toContain("DevEx Score v9");
}); });
