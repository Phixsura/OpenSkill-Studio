import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { HotReloadPanel } from "@/components/hot-reload-panel";
describe("HotReloadPanel", () => {
  it("renders", () => {
    const { container } = render(
      <HotReloadPanel totalReloads={15}
        configs={[
          { name: "app", version: 3, hash: "abc123" },
          { name: "db", version: 1, hash: "xyz789" },
        ]} />
    );
    expect(container.textContent).toContain("Hot Reload");
    expect(container.textContent).toContain("2 configs");
    expect(container.textContent).toContain("15 reloads");
    expect(container.textContent).toContain("app v3");
    expect(container.textContent).toContain("abc123");
  });
});
