import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV68 } from "@/components/platform-v68";
describe("PlatformV68", () => { it("renders", () => {
    const { container } = render(<PlatformV68 />);
    expect(container.textContent).toContain("v68");
}); });
