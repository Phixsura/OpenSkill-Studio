import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiArtStorePanel } from "@/components/fleet-ai-art-store-panel";
describe("FleetAiArtStorePanel", () => { it("renders", () => {
    const { container } = render(<FleetAiArtStorePanel stores={3} active={3} artifacts={50000} sizeTb={2000} downloads={500000} />);
    expect(container.textContent).toContain("Artifact Store");
}); });
