import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ReqReplayPanel } from "@/components/req-replay-panel";
describe("ReqReplayPanel", () => {
  it("renders", () => {
    const { container } = render(
      <ReqReplayPanel captured={500} replayed={100} maxBuffer={1000} />
    );
    expect(container.textContent).toContain("Request Replay");
    expect(container.textContent).toContain("500/1000 captured");
    expect(container.textContent).toContain("100 replayed");
  });
});
