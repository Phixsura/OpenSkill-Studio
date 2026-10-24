import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { MeshReplayPanel } from "@/components/mesh-replay-panel";
describe("MeshReplayPanel", () => {
  it("renders", () => {
    const { container } = render(
      <MeshReplayPanel captured={5000} replayed={2000} />
    );
    expect(container.textContent).toContain("Mesh Traffic Replay");
    expect(container.textContent).toContain("5,000");
    expect(container.textContent).toContain("2,000");
  });
});
