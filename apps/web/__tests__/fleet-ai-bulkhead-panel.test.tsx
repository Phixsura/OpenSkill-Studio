import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiBulkheadPanel } from "@/components/fleet-ai-bulkhead-panel";
describe("FleetAiBulkheadPanel", () => { it("renders", () => {
    const { container } = render(<FleetAiBulkheadPanel bulkheads={5} active={5} partitions={50} rejections={1000} isolation={100} />);
    expect(container.textContent).toContain("AI Bulkhead");
}); });
