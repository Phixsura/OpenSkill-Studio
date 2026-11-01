import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiFeatStorePanel } from "@/components/fleet-ai-feat-store-panel";
describe("FleetAiFeatStorePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiFeatStorePanel stores={3} active={3} features={10000} qps={500000} freshness={25} />);
    expect(container.textContent).toContain("Feature Store");
}); });
