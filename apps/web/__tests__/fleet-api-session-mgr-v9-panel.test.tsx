import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSessionMgrV9Panel } from "@/components/fleet-api-session-mgr-v9-panel";
describe("FleetApiSessionMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSessionMgrV9Panel sessions={5000} active={4500} />);
    expect(container.textContent).toContain("API Session v9");
}); });
