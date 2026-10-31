import { render } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LiveConfigViewer } from "@/components/live-config-viewer";

describe("LiveConfigViewer", () => {
  it("renders config", () => {
    const { container } = render(
      <LiveConfigViewer version={3} onReload={vi.fn()}
        config={{ debug: true, port: 8080, env: "production" }}
        history={[
          { version: 3, hash: "abc", keysChanged: ["debug"] },
          { version: 2, hash: "def", keysChanged: ["port"] },
        ]} />
    );
    expect(container.textContent).toContain("Live Config");
    expect(container.textContent).toContain("v3");
    expect(container.textContent).toContain("3 keys");
    expect(container.textContent).toContain("debug");
    expect(container.textContent).toContain("Reload");
    expect(container.textContent).toContain("Recent Changes");
  });
});
