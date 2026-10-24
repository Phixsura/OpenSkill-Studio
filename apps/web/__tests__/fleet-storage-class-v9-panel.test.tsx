import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStorageClassV9Panel } from "@/components/fleet-storage-class-v9-panel";
describe("FleetStorageClassV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetStorageClassV9Panel classes={5} volumes={200} />);
    expect(container.textContent).toContain("Storage Class v9");
}); });
