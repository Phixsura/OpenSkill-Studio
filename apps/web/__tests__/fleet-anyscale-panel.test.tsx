import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAnyscalePanel } from "@/components/fleet-anyscale-panel";
describe("FleetAnyscalePanel", () => { it("renders", () => {
    const { container } = render(<FleetAnyscalePanel clusters={5} running={5} nodes={200} activeJobs={50} />);
    expect(container.textContent).toContain("Anyscale");
}); });
