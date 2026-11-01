import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GwConnTrackPanel } from "@/components/gw-conn-track-panel";
describe("GwConnTrackPanel", () => {
  it("renders", () => {
    const { container } = render(
      <GwConnTrackPanel active={500} totalConnections={600} uniqueClients={200}
        byProtocol={{ "HTTP/2": 400, "HTTP/1.1": 100 }}
        topClients={[{ ip: "1.1.1.1", count: 50 }, { ip: "2.2.2.2", count: 30 }]} />
    );
    expect(container.textContent).toContain("Gateway Connections");
    expect(container.textContent).toContain("500 active / 600 total");
    expect(container.textContent).toContain("200 clients");
    expect(container.textContent).toContain("HTTP/2: 400");
    expect(container.textContent).toContain("1.1.1.1");
    expect(container.textContent).toContain("50 conn");
  });
});
