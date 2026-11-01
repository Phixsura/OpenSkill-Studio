import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiPlatStorageV4Panel } from "@/components/fleet-ai-plat-storage-v4-panel";
describe("FleetAiPlatStorageV4Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiPlatStorageV4Panel systems={5} active={5} total={500} used={300} iops={50000000} />);
    expect(container.textContent).toContain("AI Storage v4");
}); });
