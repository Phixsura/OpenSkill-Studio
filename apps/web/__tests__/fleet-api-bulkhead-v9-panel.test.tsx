import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiBulkheadV9Panel } from "@/components/fleet-api-bulkhead-v9-panel";
describe("FleetApiBulkheadV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiBulkheadV9Panel bulkheads={20} rejections={0} />);
    expect(container.textContent).toContain("API Bulkhead v9");
}); });
