import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDependencyV9Panel } from "@/components/fleet-api-dependency-v9-panel";
describe("FleetApiDependencyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDependencyV9Panel apis={100} circular={0} />);
    expect(container.textContent).toContain("API Dependency v9");
}); });
