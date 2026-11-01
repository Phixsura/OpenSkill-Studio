import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ImageGallery } from "@/components/image-gallery";

describe("ImageGallery", () => {
  const images = [
    { src: "https://example.com/a.png", alt: "Shot 1", caption: "Dashboard" },
    { src: "https://example.com/b.png", alt: "Shot 2", caption: "" },
  ];
  it("renders grid", () => {
    const { container } = render(<ImageGallery images={images} />);
    const imgs = container.querySelectorAll("img");
    expect(imgs.length).toBe(2);
    expect(container.textContent).toContain("Dashboard");
  });
  it("opens lightbox", () => {
    const { container } = render(<ImageGallery images={images} />);
    fireEvent.click(container.querySelectorAll("button")[0]);
    // lightbox overlay should appear with close button
    expect(container.querySelector(".fixed")).toBeTruthy();
  });
});
