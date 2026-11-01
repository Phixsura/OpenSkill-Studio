import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiReliabilityScoreV9Panel } from "@/components/fleet-api-reliability-score-v9-panel";
describe("FleetApiReliabilityScoreV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiReliabilityScoreV9Panel services={200} score={99.99} />);
    expect(container.textContent).toContain("Reliability Score v9");
}); });
