import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { TruncatedText } from "@/components/truncated-text";

describe("TruncatedText", () => {
  it("renders truncated", () => {
    const { container } = render(
      <TruncatedText text="Hello..." fullText="Hello World Complete" truncated={true} />
    );
    expect(container.textContent).toContain("Hello...");
    expect(container.textContent).toContain("Show more");
  });
  it("expands on click", () => {
    const { container } = render(
      <TruncatedText text="Short..." fullText="Full long text here" truncated={true} />
    );
    fireEvent.click(container.querySelector("button")!);
    expect(container.textContent).toContain("Full long text here");
    expect(container.textContent).toContain("Show less");
  });
  it("no button when not truncated", () => {
    const { container } = render(
      <TruncatedText text="Hello" fullText="Hello" truncated={false} />
    );
    expect(container.querySelector("button")).toBeFalsy();
  });
});
