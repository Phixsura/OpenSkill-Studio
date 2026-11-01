import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetSbomTrackerV9Panel } from "@/components/fleet-sbom-tracker-v9-panel";
describe("FleetSbomTrackerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetSbomTrackerV9Panel artifacts={100} components={5000} />);
    expect(container.textContent).toContain("SBOM Tracker v9");
}); });
