import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmbedCodeGenerator } from "@/components/embed-code-generator";

const options = { extensionId: "ext-1", themes: ["light", "dark", "auto"], sizes: ["small", "medium", "large"] };

describe("EmbedCodeGenerator", () => {
  it("renders generator", () => {
    const { container } = render(<EmbedCodeGenerator options={options} />);
    expect(container.textContent).toContain("Embed Widget");
    expect(container.textContent).toContain("iframe");
    expect(container.querySelector("pre")).toBeTruthy();
  });
  it("switches format", () => {
    const { container } = render(<EmbedCodeGenerator options={options} />);
    const htmlBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "html" || b.textContent === "HTML");
    if (htmlBtn) fireEvent.click(htmlBtn);
    expect(container.querySelector("pre")?.textContent).toContain("data-osk-ext");
  });
});
