--- app.mjs	2023-06-20 14:17:50
+++ app-2.3.0.mjs	2023-06-20 14:18:55
@@ -34,7 +34,7 @@
 fastify.register(fastifyCookie, { secret : crypto.randomBytes(20).toString('hex') }) // for cookies signature
 await fastify.register(fastifyCsrfProtection, { 
   cookieOpts: { signed: true },
-  // csrfOpts: { hmacKey: crypto.randomBytes(20).toString('hex') },
+  csrfOpts: { hmacKey: crypto.randomBytes(20).toString('hex') },
   getUserInfo (req) { return  req.user ?? "default" } 
 })
 
