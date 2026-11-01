import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetObjectStorageV9Panel } from "@/components/fleet-object-storage-v9-panel";
describe("FleetObjectStorageV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetObjectStorageV9Panel buckets={20} sizeTb={100} />);
    expect(container.textContent).toContain("Object Storage v9");
}); });
