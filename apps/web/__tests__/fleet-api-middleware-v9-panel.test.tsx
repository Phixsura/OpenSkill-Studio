import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiMiddlewareV9Panel } from "@/components/fleet-api-middleware-v9-panel";
describe("FleetApiMiddlewareV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiMiddlewareV9Panel middlewares={20} overhead={1.5} />);
    expect(container.textContent).toContain("API Middleware v9");
}); });
