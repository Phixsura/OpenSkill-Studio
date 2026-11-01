import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiProxyV9Panel } from "@/components/fleet-api-proxy-v9-panel";
describe("FleetApiProxyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiProxyV9Panel proxies={10} rps={500000} />);
    expect(container.textContent).toContain("API Proxy v9");
}); });
