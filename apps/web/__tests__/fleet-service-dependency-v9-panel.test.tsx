import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceDependencyV9Panel } from "@/components/fleet-service-dependency-v9-panel";
describe("FleetServiceDependencyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceDependencyV9Panel deps={200} circular={0} />);
    expect(container.textContent).toContain("Service Dependency v9");
}); });
