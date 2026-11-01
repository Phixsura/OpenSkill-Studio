import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV18 } from "@/components/platform-v18";
describe("PlatformV18", () => { it("renders", () => {
    const { container } = render(<PlatformV18 />);
    expect(container.textContent).toContain("v18.0");
}); });
