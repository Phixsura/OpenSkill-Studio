import { render, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmbedWidgetConfigurator } from "@/components/embed-widget-configurator";

describe("EmbedWidgetConfigurator", () => {
  it("renders", () => {
    const { container } = render(
      <EmbedWidgetConfigurator appName="Auth SDK" iframeCode='<iframe src="x">'
        scriptCode='<script src="y">' previewUrl="https://x.com" onCopy={vi.fn()} />
    );
    expect(container.textContent).toContain("Embed Auth SDK");
    expect(container.textContent).toContain("iFrame");
    expect(container.textContent).toContain("Script Tag");
    expect(container.textContent).toContain('<iframe src="x">');
  });
  it("copy", () => {
    const fn = vi.fn();
    const { container } = render(
      <EmbedWidgetConfigurator appName="X" iframeCode="<iframe>" scriptCode="<script>"
        previewUrl="" onCopy={fn} />
    );
    fireEvent.click(Array.from(container.querySelectorAll("button")).find(b => b.textContent === "Copy")!);
    expect(fn).toHaveBeenCalledWith("<iframe>");
  });
});
