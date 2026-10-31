import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCircleciPanel } from "@/components/fleet-circleci-panel";
describe("FleetCircleciPanel", () => { it("renders", () => {
    const { container } = render(<FleetCircleciPanel total={100} success={90} creditsUsed={5000} successRate={90} />);
    expect(container.textContent).toContain("CircleCI");
    expect(container.textContent).toContain("90% success");
}); });
