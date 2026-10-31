import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformApex } from "@/components/platform-apex";
describe("PlatformApex", () => { it("renders", () => {
    const { container } = render(<PlatformApex />);
    expect(container.textContent).toContain("APEX");
    expect(container.textContent).toContain("DORA Elite");
}); });
