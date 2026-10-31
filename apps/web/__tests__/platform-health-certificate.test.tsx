import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformHealthCertificate } from "@/components/platform-health-certificate";
describe("PlatformHealthCertificate", () => { it("renders", () => {
    const { container } = render(<PlatformHealthCertificate />);
    expect(container.textContent).toContain("PLATINUM");
    expect(container.textContent).toContain("DORA ELITE");
}); });
