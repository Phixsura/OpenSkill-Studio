import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { LogoPlaceholder } from "@/components/logo-placeholder";

describe("LogoPlaceholder", () => {
  it("renders initials", () => {
    const { container } = render(
      <LogoPlaceholder initials="AS" gradient="from-blue-500 to-purple-600"
        size={64} fontSize={32} shape="rounded-xl" />
    );
    expect(container.textContent).toContain("AS");
  });
  it("renders image", () => {
    const { container } = render(
      <LogoPlaceholder initials="X" gradient="" size={48} fontSize={24}
        shape="rounded-lg" imageUrl="https://example.com/logo.png" />
    );
    expect(container.querySelector("img")).toBeTruthy();
  });
});
