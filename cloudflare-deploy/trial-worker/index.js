const TRIAL_DAYS = 7;

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { ...CORS, "Content-Type": "application/json" },
  });
}

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    const url = new URL(request.url);

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

    return json({ error: "not found" }, 404);
  },
};
