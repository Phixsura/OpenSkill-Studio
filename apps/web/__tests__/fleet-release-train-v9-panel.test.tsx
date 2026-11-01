import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetReleaseTrainV9Panel } from "@/components/fleet-release-train-v9-panel";
describe("FleetReleaseTrainV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetReleaseTrainV9Panel releases={100} avgLead={4} />);
    expect(container.textContent).toContain("Release Train v9");
}); });
