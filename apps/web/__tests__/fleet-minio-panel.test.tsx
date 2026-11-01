import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetMinioPanel } from "@/components/fleet-minio-panel";
describe("FleetMinioPanel", () => { it("renders", () => {
    const { container } = render(<FleetMinioPanel servers={4} online={4} totalTb={40} usedTb={24} usagePct={60} />);
    expect(container.textContent).toContain("MinIO");
    expect(container.textContent).toContain("60%");
}); });
