/**
 * dictate.app Affiliate Worker
 *
 * Routes:
 *   POST /api/affiliate-signup      — register new affiliate, store in KV
 *   GET  /go/:code                  — set 30-day cookie, redirect to Stripe with client_reference_id
 *   POST /api/stripe-webhook        — handle checkout.session.completed, log commission
 *   GET  /api/affiliate-dashboard/:code — return JSON stats (clicks, conversions, earned)
 *
 * KV namespace binding: AFFILIATES
 *
 * KV key schema:
 *   affiliate:{code}          → JSON affiliate record
 *   email:{email}             → code (for dedup lookup)
 *   clicks:{code}             → integer (total clicks)
 *   conversions:{code}        → JSON array of conversion objects
 */

const STRIPE_PAYMENT_LINK = "https://buy.stripe.com/8x2aEX7ree937fw6A3dwc0l";
const COMMISSION_RATE = 0.4;
const COOKIE_DAYS = 30;
const CORS_ORIGIN = "https://dictate.app";

// ─────────────────────────────────────────
//  ENTRY POINT
// ─────────────────────────────────────────

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const path = url.pathname;
    const method = request.method;

    // CORS preflight
    if (method === "OPTIONS") {
      return corsResponse(null, 204);
    }

    try {
      // POST /api/affiliate-signup
      if (method === "POST" && path === "/api/affiliate-signup") {
        return await handleSignup(request, env);
      }

      // GET /go/:code
      if (method === "GET" && path.startsWith("/go/")) {
        const code = path.slice(4).replace(/^\//, "");
        return await handleRedirect(request, env, code);
      }

      // POST /api/stripe-webhook
      if (method === "POST" && path === "/api/stripe-webhook") {
        return await handleStripeWebhook(request, env);
      }

      // GET /api/affiliate-dashboard/:code
      if (method === "GET" && path.startsWith("/api/affiliate-dashboard/")) {
        const code = path.slice("/api/affiliate-dashboard/".length);
        return await handleDashboard(request, env, code);
      }

      return jsonResponse({ error: "Not found" }, 404);
    } catch (err) {
      console.error("Worker error:", err);
      return jsonResponse({ error: "Internal server error" }, 500);
    }
  },
};

// ─────────────────────────────────────────
//  POST /api/affiliate-signup
// ─────────────────────────────────────────

async function handleSignup(request, env) {
  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ error: "Invalid JSON body" }, 400);
  }

  const { first_name, last_name, email, platform, handle, paypal_email } = body;

  if (
    !first_name ||
    !last_name ||
    !email ||
    !platform ||
    !handle ||
    !paypal_email
  ) {
    return jsonResponse({ error: "All fields are required." }, 400);
  }

  if (!isValidEmail(email) || !isValidEmail(paypal_email)) {
    return jsonResponse({ error: "Invalid email address." }, 400);
  }

  // Check if email already registered
  const emailKey = `email:${email.toLowerCase()}`;
  const existing = await env.AFFILIATES.get(emailKey);
  if (existing) {
    // Return their existing code rather than erroring
    const affiliate = await env.AFFILIATES.get(`affiliate:${existing}`);
    const parsed = affiliate ? JSON.parse(affiliate) : null;
    return jsonResponse({
      success: true,
      message: "Already registered.",
      ref_code: existing,
      dashboard_url: `https://affiliate-worker.dictate-app.workers.dev/api/affiliate-dashboard/${existing}`,
    });
  }

  // Generate unique ref code from name + random suffix
  const baseCode = slugify(`${first_name}${last_name}`).slice(0, 12);
  const suffix = randomId(4);
  const ref_code = `${baseCode}-${suffix}`.toLowerCase();

  const affiliateRecord = {
    ref_code,
    first_name,
    last_name,
    email: email.toLowerCase(),
    platform,
    handle,
    paypal_email: paypal_email.toLowerCase(),
    status: "pending", // pending → approved by admin
    created_at: new Date().toISOString(),
  };

  // Store affiliate record
  await env.AFFILIATES.put(
    `affiliate:${ref_code}`,
    JSON.stringify(affiliateRecord),
  );
  // Store email → code mapping
  await env.AFFILIATES.put(emailKey, ref_code);
  // Initialise click counter
  await env.AFFILIATES.put(`clicks:${ref_code}`, "0");
  // Initialise conversions list
  await env.AFFILIATES.put(`conversions:${ref_code}`, JSON.stringify([]));

  return jsonResponse({
    success: true,
    message: "Application received. We'll email you within 24 hours.",
    ref_code,
    affiliate_link: `https://dictate.app/go/${ref_code}`,
    dashboard_url: `https://affiliate-worker.dictate-app.workers.dev/api/affiliate-dashboard/${ref_code}`,
  });
}

// ─────────────────────────────────────────
//  GET /go/:code  (click tracking + redirect)
// ─────────────────────────────────────────

async function handleRedirect(request, env, code) {
  if (!code) {
    return Response.redirect(STRIPE_PAYMENT_LINK, 302);
  }

  // Verify the affiliate exists
  const affiliateRaw = await env.AFFILIATES.get(`affiliate:${code}`);
  if (!affiliateRaw) {
    // Still redirect — don't break the link, just skip attribution
    return Response.redirect(STRIPE_PAYMENT_LINK, 302);
  }

  // Increment click counter (fire-and-forget — don't await to keep redirect fast)
  incrementClicks(env, code);

  // Build destination URL with client_reference_id
  const dest = new URL(STRIPE_PAYMENT_LINK);
  dest.searchParams.set("client_reference_id", code);

  // Set 30-day cookie, then redirect
  const cookieExpiry = new Date(
    Date.now() + COOKIE_DAYS * 24 * 60 * 60 * 1000,
  ).toUTCString();
  const response = Response.redirect(dest.toString(), 302);

  // Cloudflare doesn't allow mutating Response from redirect() directly,
  // so we rebuild it with the Set-Cookie header.
  const redirectResponse = new Response(null, {
    status: 302,
    headers: {
      Location: dest.toString(),
      "Set-Cookie": `ref=${code}; Expires=${cookieExpiry}; Path=/; SameSite=Lax; Secure`,
      "Cache-Control": "no-store",
    },
  });

  return redirectResponse;
}

async function incrementClicks(env, code) {
  try {
    const current = parseInt(
      (await env.AFFILIATES.get(`clicks:${code}`)) || "0",
      10,
    );
    await env.AFFILIATES.put(`clicks:${code}`, String(current + 1));
  } catch (e) {
    console.error("click increment failed:", e);
  }
}

// ─────────────────────────────────────────
//  POST /api/stripe-webhook
// ─────────────────────────────────────────

async function handleStripeWebhook(request, env) {
  const sig = request.headers.get("stripe-signature");
  const webhookSecret = env.STRIPE_WEBHOOK_SECRET;

  if (!sig || !webhookSecret) {
    return jsonResponse({ error: "Missing webhook signature" }, 400);
  }

  const rawBody = await request.text();

  // Verify HMAC-SHA256 signature
  const valid = await verifyStripeSignature(rawBody, sig, webhookSecret);
  if (!valid) {
    return jsonResponse({ error: "Invalid signature" }, 401);
  }

  let event;
  try {
    event = JSON.parse(rawBody);
  } catch {
    return jsonResponse({ error: "Invalid JSON" }, 400);
  }

  if (
    event.type !== "checkout.session.completed" &&
    event.type !== "invoice.paid"
  ) {
    return jsonResponse({ received: true });
  }

  const session = event.data.object;

  // client_reference_id holds the affiliate ref code
  const ref_code = session.client_reference_id;
  if (!ref_code) {
    return jsonResponse({ received: true, attribution: "none" });
  }

  // Verify affiliate exists
  const affiliateRaw = await env.AFFILIATES.get(`affiliate:${ref_code}`);
  if (!affiliateRaw) {
    return jsonResponse({ received: true, attribution: "unknown_code" });
  }

  // Calculate commission
  const amountTotal = session.amount_total || 0; // in cents
  const currency = session.currency || "usd";
  const commissionCents = Math.round(amountTotal * COMMISSION_RATE);
  const commissionDollars = (commissionCents / 100).toFixed(2);

  // Build conversion record
  const conversion = {
    id: event.id,
    type: event.type,
    stripe_session_id: session.id,
    customer_email: session.customer_details?.email || null,
    amount_total_cents: amountTotal,
    commission_cents: commissionCents,
    commission_dollars: commissionDollars,
    currency,
    recorded_at: new Date().toISOString(),
  };

  // Append to conversions list
  try {
    const existingRaw = await env.AFFILIATES.get(`conversions:${ref_code}`);
    const existing = existingRaw ? JSON.parse(existingRaw) : [];
    existing.push(conversion);
    await env.AFFILIATES.put(
      `conversions:${ref_code}`,
      JSON.stringify(existing),
    );
  } catch (e) {
    console.error("Failed to log conversion:", e);
    return jsonResponse({ error: "Failed to log conversion" }, 500);
  }

  return jsonResponse({
    received: true,
    attribution: ref_code,
    commission_dollars: commissionDollars,
  });
}

// ─────────────────────────────────────────
//  GET /api/affiliate-dashboard/:code
// ─────────────────────────────────────────

async function handleDashboard(request, env, code) {
  if (!code) {
    return jsonResponse({ error: "Missing affiliate code" }, 400);
  }

  const affiliateRaw = await env.AFFILIATES.get(`affiliate:${code}`);
  if (!affiliateRaw) {
    return jsonResponse({ error: "Affiliate not found" }, 404);
  }

  const affiliate = JSON.parse(affiliateRaw);
  const clicks = parseInt(
    (await env.AFFILIATES.get(`clicks:${code}`)) || "0",
    10,
  );
  const conversionsRaw = await env.AFFILIATES.get(`conversions:${code}`);
  const conversions = conversionsRaw ? JSON.parse(conversionsRaw) : [];

  const totalEarnedCents = conversions.reduce(
    (sum, c) => sum + (c.commission_cents || 0),
    0,
  );
  const totalEarnedDollars = (totalEarnedCents / 100).toFixed(2);

  // Group by month for summary
  const monthlyMap = {};
  conversions.forEach((c) => {
    const month = c.recorded_at.slice(0, 7); // "YYYY-MM"
    if (!monthlyMap[month])
      monthlyMap[month] = { conversions: 0, commission_cents: 0 };
    monthlyMap[month].conversions += 1;
    monthlyMap[month].commission_cents += c.commission_cents || 0;
  });

  const monthly_summary = Object.entries(monthlyMap)
    .sort(([a], [b]) => b.localeCompare(a))
    .map(([month, data]) => ({
      month,
      conversions: data.conversions,
      earned_dollars: (data.commission_cents / 100).toFixed(2),
    }));

  return jsonResponse({
    affiliate: {
      name: `${affiliate.first_name} ${affiliate.last_name}`,
      email: affiliate.email,
      platform: affiliate.platform,
      ref_code: affiliate.ref_code,
      status: affiliate.status,
      affiliate_link: `https://dictate.app/go/${code}`,
      created_at: affiliate.created_at,
    },
    stats: {
      clicks,
      conversions: conversions.length,
      total_earned_dollars: totalEarnedDollars,
      commission_rate: "40%",
    },
    monthly_summary,
    recent_conversions: conversions
      .slice(-10)
      .reverse()
      .map((c) => ({
        date: c.recorded_at.slice(0, 10),
        amount_dollars: (c.amount_total_cents / 100).toFixed(2),
        commission_dollars: c.commission_dollars,
        currency: c.currency,
      })),
  });
}

// ─────────────────────────────────────────
//  STRIPE SIGNATURE VERIFICATION (HMAC-SHA256)
// ─────────────────────────────────────────

async function verifyStripeSignature(payload, sigHeader, secret) {
  try {
    // Stripe sig header format: "t=timestamp,v1=signature,v1=..."
    const parts = sigHeader.split(",");
    const tPart = parts.find((p) => p.startsWith("t="));
    const v1Parts = parts.filter((p) => p.startsWith("v1="));

    if (!tPart || v1Parts.length === 0) return false;

    const timestamp = tPart.slice(2);
    const expectedSigs = v1Parts.map((p) => p.slice(3));

    // Signed payload = timestamp + "." + raw body
    const signedPayload = `${timestamp}.${payload}`;

    // Import secret key
    const encoder = new TextEncoder();
    const keyData = encoder.encode(secret);
    const cryptoKey = await crypto.subtle.importKey(
      "raw",
      keyData,
      { name: "HMAC", hash: "SHA-256" },
      false,
      ["sign"],
    );

    // Compute HMAC
    const signatureBuffer = await crypto.subtle.sign(
      "HMAC",
      cryptoKey,
      encoder.encode(signedPayload),
    );

    // Convert to hex
    const computed = Array.from(new Uint8Array(signatureBuffer))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");

    // Compare with constant-time equality
    return expectedSigs.some((sig) => timingSafeEqual(computed, sig));
  } catch (e) {
    console.error("Signature verification error:", e);
    return false;
  }
}

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let result = 0;
  for (let i = 0; i < a.length; i++) {
    result |= a.charCodeAt(i) ^ b.charCodeAt(i);
  }
  return result === 0;
}

// ─────────────────────────────────────────
//  HELPERS
// ─────────────────────────────────────────

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": CORS_ORIGIN,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

function corsResponse(body, status = 200) {
  return new Response(body, {
    status,
    headers: {
      "Access-Control-Allow-Origin": CORS_ORIGIN,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}

function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function slugify(str) {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]/g, "")
    .slice(0, 20);
}

function randomId(len) {
  const chars = "abcdefghijklmnopqrstuvwxyz0123456789";
  let result = "";
  for (let i = 0; i < len; i++) {
    result += chars[Math.floor(Math.random() * chars.length)];
  }
  return result;
}
