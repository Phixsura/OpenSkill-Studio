import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformZenMaster } from "@/components/platform-zenmaster";
describe("PlatformZenMaster", () => { it("renders", () => {
    const { container } = render(<PlatformZenMaster />);
    expect(container.textContent).toContain("ZEN MASTER");
    expect(container.textContent).toContain("PERFECTLY RAKED");
}); });
