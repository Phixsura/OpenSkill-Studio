import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetStorageTieringV9Panel } from "@/components/fleet-storage-tiering-v9-panel";
describe("FleetStorageTieringV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetStorageTieringV9Panel hot={100} warm={300} cold={500} />);
    expect(container.textContent).toContain("Storage Tiering v9");
}); });
