/* Keeps the pairing tool openable with no signal.
 *
 * The club plays in a bar. The tool is one self-contained file, but a page that
 * has to be fetched is a page that fails when the wifi does, and finding that
 * out with fourteen people waiting is the worst possible moment.
 *
 * Network first with a short timeout, so a working connection always gets the
 * current build and a dead one still gets the last good copy. Only the pairing
 * tool is cached: the public ladder is deliberately left alone so members are
 * never shown a stale board.
 */
const CACHE = "kava-tool-v1";
const TOOL = "kava-pairings.html";

self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.add(TOOL)).catch(() => {}));
});

self.addEventListener("activate", e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", e => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET") return;
  if (!url.pathname.endsWith("/" + TOOL)) return;   // the tool, and nothing else

  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      // a slow connection is worse than no connection: cap the wait
      const net = await Promise.race([
        fetch(e.request),
        new Promise((_, rej) => setTimeout(() => rej(new Error("slow")), 4000))
      ]);
      if (net && net.ok) cache.put(TOOL, net.clone());
      return net;
    } catch (err) {
      const hit = await cache.match(TOOL);
      if (hit) return hit;
      throw err;
    }
  })());
});
