import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetAiStorageV8Panel } from "@/components/fleet-ai-storage-v8-panel";
describe("FleetAiStorageV8Panel", () => { it("renders", () => {
    const { container } = render(<FleetAiStorageV8Panel systems={5} active={5} totalEb={50} iops={5000000000} durability={99.999999999} />);
    expect(container.textContent).toContain("Storage v8");
}); });
