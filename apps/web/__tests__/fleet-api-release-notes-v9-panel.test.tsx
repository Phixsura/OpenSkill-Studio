import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiReleaseNotesV9Panel } from "@/components/fleet-api-release-notes-v9-panel";
describe("FleetApiReleaseNotesV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiReleaseNotesV9Panel releases={100} features={500} />);
    expect(container.textContent).toContain("Release Notes v9");
}); });
