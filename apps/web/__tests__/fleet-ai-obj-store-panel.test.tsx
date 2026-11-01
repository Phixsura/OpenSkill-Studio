import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiObjStorePanel } from "@/components/fleet-ai-obj-store-panel";
describe("FleetAiObjStorePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiObjStorePanel stores={4} active={4} objects={500000000} sizeTb={2000} ops={200000000} />);
    expect(container.textContent).toContain("Object Storage");
}); });
