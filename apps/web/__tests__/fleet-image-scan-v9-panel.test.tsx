import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FleetImageScanV9Panel } from "@/components/fleet-image-scan-v9-panel";
describe("FleetImageScanV9Panel", () => { it("renders", () => {
    const { container } = render(<FleetImageScanV9Panel images={200} clean={195} />);
    expect(container.textContent).toContain("Image Scan v9");
}); });
