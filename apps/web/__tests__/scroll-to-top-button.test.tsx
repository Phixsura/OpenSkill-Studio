import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScrollToTopButton } from "@/components/scroll-to-top-button";

describe("ScrollToTopButton", () => {
  it("hidden initially (scrollY = 0)", () => {
    const { container } = render(
      <ScrollToTopButton showThreshold={300} positionClass="fixed bottom-6 right-6" smooth={true} />
    );
    // scrollY is 0 in jsdom, so button is hidden
    expect(container.querySelector("button")).toBeFalsy();
  });
});
