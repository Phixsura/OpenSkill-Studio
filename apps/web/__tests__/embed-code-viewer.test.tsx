import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { EmbedCodeViewer } from "@/components/embed-code-viewer";

describe("EmbedCodeViewer", () => {
  it("shows iframe by default", () => {
    const { container } = render(
      <EmbedCodeViewer iframe="<iframe src='x'></iframe>" badge="<a>badge</a>" directLink="https://x.com" />
    );
    expect(container.textContent).toContain("<iframe");
  });
  it("switches to badge", () => {
    const { container } = render(
      <EmbedCodeViewer iframe="<iframe/>" badge="<a>BADGE</a>" directLink="https://x.com" />
    );
    const badgeBtn = Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Badge")!;
    fireEvent.click(badgeBtn);
    expect(container.textContent).toContain("BADGE");
  });
});
