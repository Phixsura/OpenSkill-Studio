import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformV63 } from "@/components/platform-v63";
describe("PlatformV63", () => { it("renders", () => {
    const { container } = render(<PlatformV63 />);
    expect(container.textContent).toContain("v63");
}); });
