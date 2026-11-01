import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiCompressionV9Panel } from "@/components/fleet-api-compression-v9-panel";
describe("FleetApiCompressionV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiCompressionV9Panel endpoints={100} saved={5000} />);
    expect(container.textContent).toContain("API Compression v9");
}); });
