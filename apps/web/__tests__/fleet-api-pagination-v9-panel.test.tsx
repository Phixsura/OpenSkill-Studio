import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiPaginationV9Panel } from "@/components/fleet-api-pagination-v9-panel";
describe("FleetApiPaginationV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiPaginationV9Panel endpoints={50} cursor={30} />);
    expect(container.textContent).toContain("API Pagination v9");
}); });
