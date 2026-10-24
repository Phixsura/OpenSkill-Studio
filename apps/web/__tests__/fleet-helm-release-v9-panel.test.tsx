import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetHelmReleaseV9Panel } from "@/components/fleet-helm-release-v9-panel";
describe("FleetHelmReleaseV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetHelmReleaseV9Panel releases={50} deployed={48} />);
    expect(container.textContent).toContain("Helm Release v9");
}); });
