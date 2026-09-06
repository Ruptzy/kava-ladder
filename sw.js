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
const CACHE = "kava-tool-v2";
const TOOL = "kava-pairings.html";
// the icons and manifest too, or an installed app opens to a blank icon offline
const ALSO = ["pairings.webmanifest", "icons/icon-192.png", "icons/icon-512.png",
              "icons/maskable-192.png", "icons/maskable-512.png"];

self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(c => c.addAll([TOOL].concat(ALSO))).catch(() => {}));
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
  const mine = url.pathname.endsWith("/" + TOOL) ||
               ALSO.some(a => url.pathname.endsWith("/" + a));
  if (!mine) return;   // the tool and its icons, and nothing else

  e.respondWith((async () => {
    const cache = await caches.open(CACHE);
    try {
      // a slow connection is worse than no connection: cap the wait
      const net = await Promise.race([
        fetch(e.request),
        new Promise((_, rej) => setTimeout(() => rej(new Error("slow")), 4000))
      ]);
      if (net && net.ok) cache.put(e.request, net.clone());
      return net;
    } catch (err) {
      const hit = await cache.match(e.request) || await cache.match(TOOL);
      if (hit) return hit;
      throw err;
    }
  })());
});
