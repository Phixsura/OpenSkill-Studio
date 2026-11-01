import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiConsumerV9Panel } from "@/components/fleet-api-consumer-v9-panel";
describe("FleetApiConsumerV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiConsumerV9Panel consumers={200} calls={1000000} />);
    expect(container.textContent).toContain("API Consumer v9");
}); });
