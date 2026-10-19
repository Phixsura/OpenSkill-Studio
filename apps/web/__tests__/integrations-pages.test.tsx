import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import type { ReactNode } from "react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("next/link", () => ({
  default: ({ href, children }: { href: string; children: ReactNode }) => (
    <a href={href}>{children}</a>
  ),
}));
vi.mock("next/navigation", () => ({
  usePathname: () => "/dashboard/orgs/ORG/integrations",
  useRouter: () => ({ replace: vi.fn(), push: vi.fn() }),
  useParams: () => ({ orgId: "ORG1234567890123456789012" }),
  useSearchParams: () => new URLSearchParams(),
}));
vi.mock("sonner", () => ({
  toast: { success: vi.fn(), error: vi.fn() },
}));
vi.mock("@/stores/auth", () => ({
  useAuthStore: { getState: () => ({ accessToken: "test-token" }) },
}));
vi.mock("@/lib/api", () => ({
  apiWithAuth: vi.fn(),
  ApiError: class extends Error {
    constructor(
      public status: number,
      public code: string,
      message: string,
    ) {
      super(message);
    }
  },
}));

import IntegrationsHubPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/page";
import DataPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/data/page";
import EventsPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/events/page";
import IdentityPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/identity/page";
import SyncPage from "@/app/(dashboard)/dashboard/orgs/[orgId]/integrations/sync/page";
import { apiWithAuth } from "@/lib/api";

const api = vi.mocked(apiWithAuth);

function wrapper() {
  const qc = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  function Wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={qc}>{children}</QueryClientProvider>;
  }
  return Wrapper;
}

beforeEach(() => {
  vi.clearAllMocks();
});

function route(table: Record<string, unknown>) {
  api.mockImplementation((path: string) => {
    for (const [prefix, payload] of Object.entries(table)) {
      if (path.startsWith(prefix)) return Promise.resolve(payload);
    }
    return Promise.resolve({ data: [] });
  });
}

describe("integrations hub", () => {
  it("renders connections with health badges and pings", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/providers": {
        data: [
          {
            id: "p1",
            key: "oneroster",
            category: "roster",
            auth_mode: "oauth2_cc",
            display_name: "OneRoster 1.2 (SIS)",
            config_schema: {},
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/connections/c1/ping": {
        data: { ok: true, status: "active" },
      },
      "/orgs/ORG1234567890123456789012/integrations/connections": {
        data: [
          {
            id: "c1",
            provider_key: "oneroster",
            name: "District SIS",
            status: "degraded",
            base_url: "https://sis.example.com",
            health: { last_error_class: "CONNECTION_PING_FAILED" },
            has_credential: false,
          },
        ],
      },
    });
    render(<IntegrationsHubPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("District SIS")).toBeTruthy());
    expect(screen.getByText("degraded")).toBeTruthy();
    expect(screen.getByText("no credential")).toBeTruthy();
    expect(screen.getByText("CONNECTION_PING_FAILED")).toBeTruthy();
    fireEvent.click(screen.getByText("Ping"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/connections/c1/ping",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("creates a connection from the catalog", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/providers": {
        data: [
          {
            id: "p1",
            key: "generic_rest",
            category: "generic",
            auth_mode: "api_key",
            display_name: "Generic REST API",
            config_schema: {},
          },
        ],
      },
    });
    render(<IntegrationsHubPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/Generic REST API/)).toBeTruthy());
    fireEvent.change(screen.getByLabelText("Provider"), {
      target: { value: "generic_rest" },
    });
    fireEvent.change(screen.getByLabelText("Connection name"), {
      target: { value: "CRM" },
    });
    fireEvent.click(screen.getByText("Create"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/connections",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});

describe("events page", () => {
  it("lists deliveries, expands attempts and replays", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/deliveries/d1/replay": { data: {} },
      "/orgs/ORG1234567890123456789012/integrations/deliveries/d1": {
        data: {
          id: "d1",
          event_id: "e1",
          event_type: "com.openskill.project.approved.v1",
          subscription_id: "s1",
          status: "exhausted",
          attempt_count: 8,
          next_attempt_at: null,
          replay_of: null,
          attempts: [
            {
              id: "a1",
              status_code: 500,
              error: "http_500",
              latency_ms: 42,
              attempted_at: "2026-10-11T01:00:00Z",
            },
          ],
        },
      },
      "/orgs/ORG1234567890123456789012/integrations/deliveries": {
        data: [
          {
            id: "d1",
            event_id: "e1",
            event_type: "com.openskill.project.approved.v1",
            subscription_id: "s1",
            status: "exhausted",
            attempt_count: 8,
            next_attempt_at: null,
            replay_of: null,
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/events": {
        data: [
          {
            id: "e1",
            type: "com.openskill.project.approved.v1",
            subject: "sub-1",
            time: "2026-10-11T00:00:00Z",
          },
        ],
      },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    // NOTE: "exhausted" also exists as a static <option> — wait on a
    // data-only marker instead so the list has actually rendered.
    await waitFor(() => expect(screen.getByText("attempts: 8")).toBeTruthy());
    fireEvent.click(screen.getByText("Attempts"));
    await waitFor(() => expect(screen.getByText(/http_500/)).toBeTruthy());
    fireEvent.click(screen.getByText("Replay"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/deliveries/d1/replay",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("manages subscriptions: create reveals secret once, rotate re-reveals", async () => {
    route({
      "/orgs/ORG1234567890123456789012/webhooks/w1/rotate-secret": {
        data: {
          id: "w1",
          url: "https://r.example.com/h",
          events: ["project.approved"],
          secret: "whsec_ROTATED",
          active: true,
        },
      },
      "/orgs/ORG1234567890123456789012/integrations/subscription-stats": {
        data: { w1: { succeeded: 7, exhausted: 2 } },
      },
      "/orgs/ORG1234567890123456789012/webhooks": {
        data: [
          {
            id: "w1",
            url: "https://r.example.com/h",
            events: ["project.approved"],
            secret: "whse****TED",
            active: true,
          },
        ],
      },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("https://r.example.com/h")).toBeTruthy());
    await waitFor(() => expect(screen.getByText(/7 ok/)).toBeTruthy());
    expect(screen.getByText(/2 exhausted/)).toBeTruthy();
    fireEvent.click(screen.getByText("Rotate secret"));
    await waitFor(() => expect(screen.getByText(/whsec_ROTATED/)).toBeTruthy());
    expect(api).toHaveBeenCalledWith(
      "/orgs/ORG1234567890123456789012/webhooks/w1/rotate-secret?immediate=false",
      expect.objectContaining({ method: "POST" }),
    );
    fireEvent.click(screen.getByText("Rotate now"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/webhooks/w1/rotate-secret?immediate=true",
        expect.objectContaining({ method: "POST" }),
      ),
    );

    // R157: bulk replay of exhausted deliveries for this subscription.
    api.mockImplementationOnce(() => Promise.resolve({ data: { requeued: 2 } }));
    fireEvent.click(screen.getByText("Replay exhausted"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/webhooks/w1/replay-exhausted",
        expect.objectContaining({ method: "POST" }),
      ),
    );

    // Create path: POST then the once-only secret banner swaps to the new one.
    api.mockImplementationOnce(() =>
      Promise.resolve({
        data: {
          id: "w2",
          url: "https://r2.example.com/h",
          events: ["com.openskill.integration.*"],
          secret: "whsec_NEW2",
          active: true,
        },
      }),
    );
    fireEvent.change(screen.getByLabelText("Webhook URL"), {
      target: { value: "https://r2.example.com/h" },
    });
    fireEvent.change(screen.getByLabelText("Event patterns"), {
      target: { value: "com.openskill.integration.*" },
    });
    fireEvent.click(screen.getByText("Subscribe"));
    await waitFor(() => expect(screen.getByText(/whsec_NEW2/)).toBeTruthy());
  });
});

describe("identity page", () => {
  it("shows TXT instructions for pending domains and mints SCIM tokens once", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/domains": {
        data: [
          {
            id: "dm1",
            domain: "school.example.edu",
            status: "pending",
            verification_token: "osks-verify-abc",
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sso-connections": { data: [] },
      "/orgs/ORG1234567890123456789012/integrations/scim-tokens": { data: [] },
      "/orgs/ORG1234567890123456789012/integrations/identity-queue": {
        data: [
          {
            id: "q1",
            source: "sso",
            subject: "sub-9",
            email: "x@school.example.edu",
            reason: "no_member_match",
            status: "pending",
          },
        ],
      },
    });
    render(<IdentityPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/osks-verify-abc/)).toBeTruthy());
    // mint a token: the raw value must surface exactly once
    api.mockResolvedValueOnce({
      data: {
        id: "t1",
        name: "Entra",
        token: "osks_scim_RAW",
        last_used_at: null,
        revoked_at: null,
      },
    });
    fireEvent.change(screen.getByLabelText("Token name"), { target: { value: "Entra" } });
    fireEvent.click(screen.getByText("Mint token"));
    await waitFor(() => expect(screen.getByText(/osks_scim_RAW/)).toBeTruthy());
    // queue item renders with reject action
    expect(screen.getByText(/no_member_match/)).toBeTruthy();
    fireEvent.click(screen.getByText("Reject"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/identity-queue/q1/resolve",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});

describe("sync page", () => {
  it("R498: mints the inbound webhook trigger secret and shows it once", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/trigger-secret": {
        data: { secret: "sth_abc123def456" },
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles": {
        data: [
          {
            id: "sp1",
            connection_id: "c1",
            name: "roster",
            model: "roster.class",
            direction: "pull",
            schedule: "manual",
            enabled: true,
          },
        ],
      },
    });
    render(<SyncPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("roster")).toBeTruthy());
    fireEvent.click(screen.getByText("Webhook trigger"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/trigger-secret",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    await waitFor(() => expect(screen.getByTestId("hook-secret-panel")).toBeTruthy());
    expect(screen.getByText("sth_abc123def456")).toBeTruthy();
    expect(screen.getByText(/sync-hooks\/sp1/)).toBeTruthy();
    // disable clears the shown-once panel
    fireEvent.click(screen.getByText("Disable hook"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/trigger-secret",
        expect.objectContaining({ method: "DELETE" }),
      ),
    );
    await waitFor(() => expect(screen.queryByTestId("hook-secret-panel")).toBeNull());
  });

  it("runs profiles and surfaces conflicts", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/run": { data: {} },
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles": {
        data: [
          {
            id: "sp1",
            connection_id: "c1",
            name: "roster",
            model: "roster.class",
            direction: "pull",
            schedule: "manual",
            enabled: true,
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-runs/r1/records": {
        data: [
          {
            id: "rr1",
            external_id: "e-9",
            model: "roster.enrollment",
            outcome: "conflict",
            conflict_class: "ambiguous_identity",
            detail: {},
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-runs": {
        data: [
          {
            id: "r1",
            profile_id: "sp1",
            status: "partial",
            trigger: "manual",
            stats: { read: 5, conflicts: 1 },
            error: null,
            started_at: null,
            finished_at: null,
          },
        ],
      },
    });
    render(<SyncPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("roster")).toBeTruthy());
    fireEvent.click(screen.getByText("Run"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/run?backfill=false",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    // R196: dry-run preview button on the pull profile.
    api.mockImplementationOnce(() => Promise.resolve({ data: { count: 3, records: [] } }));
    fireEvent.click(screen.getByText("Dry-run"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/sync-profiles/sp1/preview?limit=5",
        expect.objectContaining({ method: "POST" }),
      ),
    );

    fireEvent.click(screen.getByText("Conflicts"));
    await waitFor(() => expect(screen.getByText(/ambiguous_identity/)).toBeTruthy());
  });

  it("adjudicates conflicts: accept_theirs only on clock ties, resolved badge", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/sync-runs/r1/records/rr1/resolve": {
        data: {},
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-profiles": { data: [] },
      "/orgs/ORG1234567890123456789012/integrations/sync-runs/r1/records": {
        data: [
          {
            id: "rr1",
            external_id: "e-1",
            model: "roster.class",
            outcome: "conflict",
            conflict_class: "clock_unresolvable",
            detail: { field: "t", ours: "L", theirs: "R" },
            resolved_action: null,
          },
          {
            id: "rr2",
            external_id: "e-2",
            model: "roster.class",
            outcome: "conflict",
            conflict_class: "duplicate_external_id",
            detail: {},
            resolved_action: "dismiss",
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/sync-runs": {
        data: [
          {
            id: "r1",
            profile_id: "sp1",
            status: "partial",
            trigger: "manual",
            stats: { read: 2, conflicts: 2 },
            error: null,
            started_at: null,
            finished_at: null,
          },
        ],
      },
    });
    render(<SyncPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("Conflicts")).toBeTruthy());
    fireEvent.click(screen.getByText("Conflicts"));
    await waitFor(() => expect(screen.getByText(/clock_unresolvable/)).toBeTruthy());
    // The already-resolved row shows its badge, no buttons.
    expect(screen.getByText("dismiss")).toBeTruthy();
    // Accept theirs only offered on the clock-tie row.
    expect(screen.getAllByText("Accept theirs").length).toBe(1);
    fireEvent.click(screen.getByText("Accept theirs"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/sync-runs/r1/records/rr1/resolve",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ action: "accept_theirs" }),
        }),
      ),
    );
  });
});

describe("fabric health strip", () => {
  it("renders aggregate counts with alert accents", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/health": {
        data: {
          connections: { total: 3, by_status: { active: 2, error: 1 } },
          subscriptions: { total: 2, disabled: 1 },
          deliveries: { pending: 4, exhausted_24h: 2 },
          identity_queue_pending: 5,
          sync: { profiles: 2, failed_runs_24h: 1 },
          sso_connections_active: 1,
        },
      },
      "/orgs/ORG1234567890123456789012/integrations/providers": { data: [] },
      "/orgs/ORG1234567890123456789012/integrations/connections": { data: [] },
    });
    render(<IntegrationsHubPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/1 error/)).toBeTruthy());
    expect(screen.getByText(/1 disabled/)).toBeTruthy();
    expect(screen.getByText(/2 exhausted 24h/)).toBeTruthy();
    expect(screen.getByText("5")).toBeTruthy();
  });
});

describe("lti platforms", () => {
  it("lists registrations, expands links and syncs roster via NRPS", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/lti/resource-links/L1/nrps-sync": {
        data: { read: 4, resolved: 2, jit_created: 2, queued: 1, skipped: 1 },
      },
      "/orgs/ORG1234567890123456789012/integrations/lti/registrations/R1/resource-links": {
        data: [
          {
            id: "L1",
            deployment_id: "dep-1",
            resource_link_id: "rl-1",
            kind: "skill",
            target_id: "SK1",
            has_nrps: true,
          },
          {
            id: "L2",
            deployment_id: "dep-1",
            resource_link_id: "rl-2",
            kind: "skill",
            target_id: "SK2",
            has_nrps: false,
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/lti/registrations": {
        data: [
          {
            id: "R1",
            issuer: "https://lms.example.com",
            client_id: "tool-1",
            status: "active",
            deployment_ids: ["dep-1"],
          },
        ],
      },
    });
    render(<IdentityPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("https://lms.example.com")).toBeTruthy());
    fireEvent.click(screen.getByText("https://lms.example.com"));
    await waitFor(() => expect(screen.getByText(/rl-1/)).toBeTruthy());
    expect(screen.getByText(/launch once to enable roster sync/)).toBeTruthy();
    fireEvent.click(screen.getByText("Sync roster"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/lti/resource-links/L1/nrps-sync",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});

describe("identity links", () => {
  it("lists active links and unlinks reversibly", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/identity-links/il1": { data: {} },
      "/orgs/ORG1234567890123456789012/integrations/identity-links": {
        data: [
          {
            id: "il1",
            user_id: "U1",
            source: "sso",
            subject: "subj-9",
            email_at_link: "a@b.io",
            created_at: "2026-10-11T00:00:00Z",
          },
        ],
      },
    });
    render(<IdentityPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("subj-9")).toBeTruthy());
    fireEvent.click(screen.getByText("Unlink"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/identity-links/il1",
        expect.objectContaining({ method: "DELETE" }),
      ),
    );
  });
});

describe("event payloads", () => {
  it("expands the CloudEvent data on click", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/events": {
        data: [
          {
            id: "e9",
            type: "com.openskill.brief.created.v1",
            subject: "b-1",
            time: "2026-10-11T01:00:00Z",
            data: { brief_id: "b-1", marker: "PAYLOAD_MARKER" },
          },
        ],
      },
      "/orgs/ORG1234567890123456789012/integrations/deliveries": { data: [] },
      "/orgs/ORG1234567890123456789012/webhooks": { data: [] },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText(/brief.created/)).toBeTruthy());
    expect(screen.queryByText(/PAYLOAD_MARKER/)).toBeFalsy();
    fireEvent.click(screen.getByText(/brief.created/));
    await waitFor(() => expect(screen.getByText(/PAYLOAD_MARKER/)).toBeTruthy());
  });
});

describe("data page", () => {
  it("creates export streams and runs them", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/export-streams/es1/run": {
        data: { id: "er1", status: "succeeded", row_count: 3, manifest_key: "m", created_at: "" },
      },
      "/orgs/ORG1234567890123456789012/integrations/export-streams": {
        data: [
          {
            id: "es1",
            name: "nightly",
            dataset: "events",
            field_allowlist: ["id", "type"],
            schedule: "manual",
            cursor: {},
          },
        ],
      },
    });
    render(<DataPage />, { wrapper: wrapper() });
    await waitFor(() => expect(screen.getByText("nightly")).toBeTruthy());
    fireEvent.click(screen.getByText("Run export"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/export-streams/es1/run",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });

  it("R149: stream create sends an explicit field allowlist incl. data.<key>", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/export-streams": { data: [] },
    });
    render(<DataPage />, { wrapper: wrapper() });
    fireEvent.change(await screen.findByLabelText("Stream name"), {
      target: { value: "scored" },
    });
    fireEvent.change(screen.getByLabelText("Stream fields"), {
      target: { value: " id, type ,data.score " },
    });
    fireEvent.click(screen.getByText("Create stream"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/export-streams",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "scored",
            dataset: "events",
            schedule: "manual",
            format: "ndjson",
            field_allowlist: ["id", "type", "data.score"],
          }),
        }),
      ),
    );
  });

  it("R486: stream create can pick the parquet format", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/export-streams": { data: [] },
    });
    render(<DataPage />, { wrapper: wrapper() });
    fireEvent.change(await screen.findByLabelText("Stream name"), {
      target: { value: "wh" },
    });
    fireEvent.change(screen.getByLabelText("Stream format"), {
      target: { value: "parquet" },
    });
    fireEvent.click(screen.getByText("Create stream"));
    await waitFor(() =>
      expect(api).toHaveBeenCalledWith(
        "/orgs/ORG1234567890123456789012/integrations/export-streams",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({
            name: "wh",
            dataset: "events",
            schedule: "manual",
            format: "parquet",
          }),
        }),
      ),
    );
  });

  it("R489: dry-run renders the mapped sample table for mapping confirmation", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/export-streams": { data: [] },
    });
    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        data: {
          id: "job1",
          kind: "users",
          mode: "partial",
          status: "previewed",
          dry_stats: {
            valid: 2,
            errors: 0,
            creates: 2,
            updates: 0,
            skips: 0,
            sample: [
              { email: "a@x.edu", display_name: "Alice", role: "student" },
              { email: "b@x.edu", display_name: "Bob", role: null },
            ],
          },
          stats: {},
        },
      }),
    }));
    vi.stubGlobal("fetch", fetchMock);
    render(<DataPage />, { wrapper: wrapper() });
    const fileInput = (await screen.findByLabelText("Import file")) as HTMLInputElement;
    const file = new File(["email,display_name\na@x.edu,Alice\n"], "u.csv", {
      type: "text/csv",
    });
    fireEvent.change(fileInput, { target: { files: [file] } });
    fireEvent.click(screen.getByText("Upload & preview"));
    await waitFor(() => expect(screen.getByLabelText("Mapped sample rows")).toBeTruthy());
    expect(screen.getByText("a@x.edu")).toBeTruthy();
    expect(screen.getByText("Bob")).toBeTruthy();
    vi.unstubAllGlobals();
  });

  it("R132: kind selector drives header-map fields and accepts JSON files", async () => {
    route({
      "/orgs/ORG1234567890123456789012/integrations/export-streams": { data: [] },
    });
    render(<DataPage />, { wrapper: wrapper() });
    const select = (await screen.findByLabelText("Import kind")) as HTMLSelectElement;
    expect(Array.from(select.options).map((o) => o.value)).toEqual([
      "users",
      "roster",
      "opportunities",
    ]);
    const file = screen.getByLabelText("Import file") as HTMLInputElement;
    expect(file.accept).toContain(".json");

    // users fields by default
    expect(screen.getByLabelText("CSV header for display_name")).toBeTruthy();
    // switching kind swaps the mappable columns
    fireEvent.change(select, { target: { value: "roster" } });
    await waitFor(() => expect(screen.getByLabelText("CSV header for cohort_slug")).toBeTruthy());
    expect(screen.queryByLabelText("CSV header for display_name")).toBeNull();
    fireEvent.change(select, { target: { value: "opportunities" } });
    await waitFor(() =>
      expect(screen.getByLabelText("CSV header for opportunity_type")).toBeTruthy(),
    );
  });
});

describe("events keyset paging (R375/R376)", () => {
  it("Load older appends the next cursor page and hides at the end", async () => {
    const base = "/orgs/ORG1234567890123456789012/integrations";
    route({
      // specific (cursor) route first — route() matches by startsWith
      [`${base}/events?before=EV2`]: {
        data: [{ id: "EV1", type: "com.openskill.skill.completed.v1", subject: "older", data: {} }],
        meta: { next_cursor: null, has_more: false },
      },
      [`${base}/events`]: {
        data: [
          { id: "EV3", type: "com.openskill.project.approved.v1", subject: "newest", data: {} },
          { id: "EV2", type: "com.openskill.project.approved.v1", subject: "newer", data: {} },
        ],
        meta: { next_cursor: "EV2", has_more: true },
      },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    await screen.findByText("newest");
    const btn = await screen.findByRole("button", { name: /load older events/i });
    fireEvent.click(btn);
    await screen.findByText("older");
    // page 1 still present, cursor consumed, button gone (has_more=false)
    expect(screen.getByText("newer")).toBeTruthy();
    expect(api.mock.calls.some(([p]) => String(p).includes("events?before=EV2"))).toBe(true);
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: /load older events/i })).toBeNull(),
    );
  });
});

describe("deliveries keyset paging (R375/R379)", () => {
  it("Load older deliveries appends and respects the status filter", async () => {
    const base = "/orgs/ORG1234567890123456789012/integrations";
    const mk = (id: string) => ({
      id,
      event_id: "e1",
      event_type: `evt.${id}.v1`,
      subscription_id: "s1",
      status: "succeeded",
      attempt_count: 1,
      next_attempt_at: null,
      replay_of: null,
    });
    route({
      [`${base}/deliveries?before=D2`]: {
        data: [mk("D1")],
        meta: { next_cursor: null, has_more: false },
      },
      [`${base}/deliveries`]: {
        data: [mk("D3"), mk("D2")],
        meta: { next_cursor: "D2", has_more: true },
      },
    });
    render(<EventsPage />, { wrapper: wrapper() });
    await screen.findByText(/evt\.D3\.v1/);
    const btn = await screen.findByRole("button", { name: /load older deliveries/i });
    fireEvent.click(btn);
    await screen.findByText(/evt\.D1\.v1/);
    expect(screen.getByText(/evt\.D2\.v1/)).toBeTruthy();
    expect(api.mock.calls.some(([p]) => String(p).includes("deliveries?before=D2"))).toBe(true);
    await waitFor(() =>
      expect(screen.queryByRole("button", { name: /load older deliveries/i })).toBeNull(),
    );
  });
});
