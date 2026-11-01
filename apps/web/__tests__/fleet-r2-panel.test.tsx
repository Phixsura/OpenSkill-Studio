import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetR2Panel } from "@/components/fleet-r2-panel";
describe("FleetR2Panel", () => { it("renders", () => {
    const { container } = render(<FleetR2Panel buckets={20} objects={50000000} storageGb={2000} requests={100000000} />);
    expect(container.textContent).toContain("R2");
}); });
