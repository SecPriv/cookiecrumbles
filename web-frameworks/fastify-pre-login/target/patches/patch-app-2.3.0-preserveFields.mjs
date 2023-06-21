--- app.mjs	2023-06-20 14:01:04
+++ app-2.3.0-preserveFields.mjs	2023-06-20 14:01:09
@@ -23,49 +23,49 @@
 import { Authenticator } from '@fastify/passport'
 
 const fastifyPassport = new Authenticator({ 
-  // // this semantics only works for @fastify/secure-session
-  // clearSessionOnLogin: true, 
-  // clearSessionIgnoreFields: ['passport', 'session', '_csrf'] 
+  // this semantics only works for @fastify/secure-session
+  clearSessionOnLogin: true, 
+  clearSessionIgnoreFields: ['passport', 'session', '_csrf'] 
 })
 
 
 
 // // CSRF-OPTION: Use with @fastify/session
 
-fastify.register(fastifyCookie, { secret : crypto.randomBytes(20).toString('hex') }) // for cookies signature
+// fastify.register(fastifyCookie, { secret : crypto.randomBytes(20).toString('hex') }) // for cookies signature
 
-import fastifySession from '@fastify/session'
-await fastify.register(fastifyCsrfProtection, { 
-    sessionPlugin: '@fastify/session',
-    // getUserInfo (req) { return  req.user ?? "default" },
-})
+// import fastifySession from '@fastify/session'
+// await fastify.register(fastifyCsrfProtection, { 
+//     sessionPlugin: '@fastify/session',
+//     // getUserInfo (req) { return  req.user ?? "default" },
+// })
 
 
-// PASSPORT-OPTION: use with @fastify/session
+// // PASSPORT-OPTION: use with @fastify/session
 
-await fastify.register(fastifySession, {
-  cookieName: 'session',
-  secret: crypto.randomBytes(20).toString('hex'),
-  cookie: { secure: false },
-  expires: 1800000
-})
+// await fastify.register(fastifySession, {
+//   cookieName: 'session',
+//   secret: crypto.randomBytes(20).toString('hex'),
+//   cookie: { secure: false },
+//   expires: 1800000
+// })
 
 ////////
 
 
-// // CSRF-OPTION: Use with @fastify/secure-session
-// import fastifySecureSession from '@fastify/secure-session'
-// await fastify.register(fastifyCsrfProtection, { 
-//     sessionPlugin: '@fastify/secure-session',
-//     // getUserInfo (req) { return  req.user ?? "default" },
-// })
+// CSRF-OPTION: Use with @fastify/secure-session
+import fastifySecureSession from '@fastify/secure-session'
+await fastify.register(fastifyCsrfProtection, { 
+    sessionPlugin: '@fastify/secure-session',
+    // getUserInfo (req) { return  req.user ?? "default" },
+})
 
 
-// // PASSPORT-OPTION: use with @fastify/secure-session
+// PASSPORT-OPTION: use with @fastify/secure-session
 
-// await fastify.register(fastifySecureSession, { 
-//   key: fs.readFileSync(path.join('/usr/src/', 'secret-key'))
-// })
+await fastify.register(fastifySecureSession, { 
+  key: fs.readFileSync(path.join('/usr/src/', 'secret-key'))
+})
 
 
 ////////
