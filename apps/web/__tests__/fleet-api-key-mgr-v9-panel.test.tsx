import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiKeyMgrV9Panel } from "@/components/fleet-api-key-mgr-v9-panel";
describe("FleetApiKeyMgrV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiKeyMgrV9Panel total={1000} active={950} />);
    expect(container.textContent).toContain("API Key Manager v9");
}); });
