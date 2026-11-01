import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetDataStreamV9Panel } from "@/components/fleet-data-stream-v9-panel";
describe("FleetDataStreamV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetDataStreamV9Panel streams={20} throughput={100000} />);
    expect(container.textContent).toContain("Data Stream v9");
}); });
