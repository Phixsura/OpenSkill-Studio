import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiSseV9Panel } from "@/components/fleet-api-sse-v9-panel";
describe("FleetApiSseV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiSseV9Panel streams={20} connections={10000} />);
    expect(container.textContent).toContain("API SSE v9");
}); });
