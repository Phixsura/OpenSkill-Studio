import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDependencyHealthV9Panel } from "@/components/fleet-api-dependency-health-v9-panel";
describe("FleetApiDependencyHealthV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDependencyHealthV9Panel deps={50} healthy={50} />);
    expect(container.textContent).toContain("Dep Health v9");
}); });
