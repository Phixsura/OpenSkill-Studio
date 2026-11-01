import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PlatformArk } from "@/components/platform-ark";
describe("PlatformArk", () => { it("renders", () => {
    const { container } = render(<PlatformArk />);
    expect(container.textContent).toContain("ARK");
    expect(container.textContent).toContain("907K");
}); });
