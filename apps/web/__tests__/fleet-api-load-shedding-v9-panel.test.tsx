import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiLoadSheddingV9Panel } from "@/components/fleet-api-load-shedding-v9-panel";
describe("FleetApiLoadSheddingV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiLoadSheddingV9Panel services={100} shedding={0} />);
    expect(container.textContent).toContain("Load Shedding v9");
}); });
