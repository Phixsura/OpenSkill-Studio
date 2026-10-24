import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV29 } from "@/components/platform-v29";
describe("PlatformV29", () => { it("renders", () => {
    const { container } = render(<PlatformV29 />);
    expect(container.textContent).toContain("v29");
}); });
