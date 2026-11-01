import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiDependencyCheckV9Panel } from "@/components/fleet-api-dependency-check-v9-panel";
describe("FleetApiDependencyCheckV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiDependencyCheckV9Panel deps={50} healthy={50} />);
    expect(container.textContent).toContain("API Dep Check v9");
}); });
