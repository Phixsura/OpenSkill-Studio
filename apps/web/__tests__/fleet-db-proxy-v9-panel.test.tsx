import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDbProxyV9Panel } from "@/components/fleet-db-proxy-v9-panel";
describe("FleetDbProxyV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDbProxyV9Panel pools={5} utilization={25} />);
    expect(container.textContent).toContain("DB Proxy v9");
}); });
