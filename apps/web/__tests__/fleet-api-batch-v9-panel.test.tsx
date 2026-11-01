import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetApiBatchV9Panel } from "@/components/fleet-api-batch-v9-panel";
describe("FleetApiBatchV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetApiBatchV9Panel batches={50} processed={50000} />);
    expect(container.textContent).toContain("API Batch v9");
}); });
