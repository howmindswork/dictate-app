const TRIAL_DAYS = 7;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, X-Internal-Secret",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

function randomSegment(len) {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789";
  let result = "";
  for (let i = 0; i < len; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}

function generateLicenseKey() {
  return `DICTATE-${randomSegment(4)}-${randomSegment(4)}-${randomSegment(4)}`;
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);

    // ── POST /api/check-trial ──────────────────────────────────────────────
    if (request.method === "POST" && url.pathname === "/api/check-trial") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid body" }, 400);
      }

      const { fingerprint } = body;
      if (!fingerprint || typeof fingerprint !== "string") {
        return json({ error: "missing fingerprint" }, 400);
      }

      const existing = await env.TRIAL_FINGERPRINTS.get(fingerprint);

      if (existing) {
        const trialStart = new Date(existing);
        const msElapsed = Date.now() - trialStart.getTime();
        const daysElapsed = msElapsed / (1000 * 60 * 60 * 24);

        if (daysElapsed >= TRIAL_DAYS) {
          return json({ expired: true, daysLeft: 0 });
        }

        const daysLeft = Math.ceil(TRIAL_DAYS - daysElapsed);
        return json({ expired: false, daysLeft });
      }

      await env.TRIAL_FINGERPRINTS.put(fingerprint, new Date().toISOString());
      return json({ expired: false, daysLeft: TRIAL_DAYS });
    }

    // ── POST /api/validate-license ─────────────────────────────────────────
    if (request.method === "POST" && url.pathname === "/api/validate-license") {
      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid body" }, 400);
      }

      const { key } = body;
      if (!key || typeof key !== "string") {
        return json({ valid: false, error: "missing key" }, 400);
      }

      const record = await env.TRIAL_FINGERPRINTS.get(`license:${key}`);
      if (!record) {
        return json({ valid: false });
      }

      let parsed;
      try {
        parsed = JSON.parse(record);
      } catch {
        return json({ valid: false });
      }

      if (!parsed.active) {
        return json({ valid: false });
      }

      return json({ valid: true, email: parsed.email });
    }

    // ── POST /api/register-license ─────────────────────────────────────────
    if (request.method === "POST" && url.pathname === "/api/register-license") {
      // Require internal secret
      const secret = request.headers.get("X-Internal-Secret");
      if (
        !secret ||
        secret !== (env.INTERNAL_SECRET || "DICTATE_INTERNAL_2026")
      ) {
        return json({ error: "unauthorized" }, 401);
      }

      let body;
      try {
        body = await request.json();
      } catch {
        return json({ error: "invalid body" }, 400);
      }

      const { email, key, fingerprint } = body;
      if (!email || !key) {
        return json({ error: "missing email or key" }, 400);
      }

      const record = {
        email,
        key,
        fingerprint: fingerprint || null,
        created: new Date().toISOString(),
        active: true,
      };

      await env.TRIAL_FINGERPRINTS.put(
        `license:${key}`,
        JSON.stringify(record),
      );

      return json({ success: true, key, email });
    }

    // ── GET /api/generate-key ──────────────────────────────────────────────
    if (request.method === "GET" && url.pathname === "/api/generate-key") {
      const secret = request.headers.get("X-Internal-Secret");
      if (
        !secret ||
        secret !== (env.INTERNAL_SECRET || "DICTATE_INTERNAL_2026")
      ) {
        return json({ error: "unauthorized" }, 401);
      }

      // Generate a unique key (retry up to 5 times to avoid collision)
      let key;
      for (let i = 0; i < 5; i++) {
        const candidate = generateLicenseKey();
        const existing = await env.TRIAL_FINGERPRINTS.get(
          `license:${candidate}`,
        );
        if (!existing) {
          key = candidate;
          break;
        }
      }

      if (!key) {
        return json({ error: "key generation failed" }, 500);
      }

      // Store a placeholder so it can be looked up later (will be populated by register-license)
      await env.TRIAL_FINGERPRINTS.put(
        `license:${key}`,
        JSON.stringify({ active: false, created: new Date().toISOString() }),
      );

      return json({ key });
    }

    return json({ error: "not found" }, 404);
  },
};
