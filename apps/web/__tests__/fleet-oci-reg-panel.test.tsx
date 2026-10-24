import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetOciRegPanel } from "@/components/fleet-oci-reg-panel";
describe("FleetOciRegPanel", () => { it("renders", () => {
    const { container } = render(<FleetOciRegPanel registries={3} healthy={3} images={1500} storageGb={500} />);
    expect(container.textContent).toContain("OCI Registry");
    expect(container.textContent).toContain("1,500 images");
}); });
