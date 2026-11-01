import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetCiBuildPanel } from "@/components/fleet-ci-build-panel";
describe("FleetCiBuildPanel", () => { it("renders", () => {
    const { container } = render(<FleetCiBuildPanel total={50} avgSec={467} slowBuilds={5} fast={false} />);
    expect(container.textContent).toContain("CI Build Time");
    expect(container.textContent).toContain("Builds too slow");
}); });
