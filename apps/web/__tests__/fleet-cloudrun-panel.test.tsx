import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCloudrunPanel } from "@/components/fleet-cloudrun-panel";
describe("FleetCloudrunPanel", () => { it("renders", () => {
    const { container } = render(<FleetCloudrunPanel services={20} active={20} revisions={100} requests={20000000} avgLatency={30} />);
    expect(container.textContent).toContain("Cloud Run");
}); });
