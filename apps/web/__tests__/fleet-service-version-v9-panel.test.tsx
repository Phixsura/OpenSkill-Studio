import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetServiceVersionV9Panel } from "@/components/fleet-service-version-v9-panel";
describe("FleetServiceVersionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetServiceVersionV9Panel services={200} latest={195} />);
    expect(container.textContent).toContain("Service Version v9");
}); });
