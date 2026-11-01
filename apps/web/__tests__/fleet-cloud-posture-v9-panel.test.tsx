import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudPostureV9Panel } from "@/components/fleet-cloud-posture-v9-panel";
describe("FleetCloudPostureV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetCloudPostureV9Panel accounts={5} score={95} />);
    expect(container.textContent).toContain("Cloud Posture v9");
}); });
