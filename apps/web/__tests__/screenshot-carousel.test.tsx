import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ScreenshotCarousel } from "@/components/screenshot-carousel";

describe("ScreenshotCarousel", () => {
  it("renders carousel", () => {
    const { container, getByText } = render(
      <ScreenshotCarousel appName="MyApp" screenshots={[
        { url: "https://cdn.example.com/1.png", alt: "Dashboard", caption: "Main view" },
        { url: "https://cdn.example.com/2.png", alt: "Settings", caption: "" },
      ]} />
    );
    expect(container.textContent).toContain("Main view");
    expect(container.textContent).toContain("1 / 2");
    fireEvent.click(getByText("→"));
    expect(container.textContent).toContain("2 / 2");
  });
});
