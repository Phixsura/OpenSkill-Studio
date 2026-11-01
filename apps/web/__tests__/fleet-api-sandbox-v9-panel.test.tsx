import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSandboxV9Panel } from "@/components/fleet-api-sandbox-v9-panel";
describe("FleetApiSandboxV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSandboxV9Panel sandboxes={50} users={30} />);
    expect(container.textContent).toContain("API Sandbox v9");
}); });
