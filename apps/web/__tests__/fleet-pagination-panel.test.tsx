import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetPaginationPanel } from "@/components/fleet-pagination-panel";
describe("FleetPaginationPanel", () => { it("renders", () => {
    const { container } = render(<FleetPaginationPanel total={15} paginated={12} cursorBased={8} unpaginated={3} />);
    expect(container.textContent).toContain("API Pagination");
    expect(container.textContent).toContain("3 unpaginated");
}); });
