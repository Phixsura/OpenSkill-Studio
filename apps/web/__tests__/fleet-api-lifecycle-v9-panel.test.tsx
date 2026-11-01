import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiLifecycleV9Panel } from "@/components/fleet-api-lifecycle-v9-panel";
describe("FleetApiLifecycleV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiLifecycleV9Panel total={30} active={25} />);
    expect(container.textContent).toContain("API Lifecycle v9");
}); });
