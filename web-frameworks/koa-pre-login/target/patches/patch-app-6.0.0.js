--- app.js	2023-06-19 11:15:07
+++ app-6.0.0.js	2023-06-19 11:17:36
@@ -71,8 +71,8 @@
         balance: balance[ctx.state.user],
         debug_sessionID: "",
         debug_csrf_secret: ctx.session.secret,
-        // 3.0.8
-        csrf_token: ctx.csrf,
+        // 5.0.1
+        csrf_token: ctx.state._csrf,
     });
 });
 
@@ -94,6 +94,7 @@
 router.post('/login', passport.authenticate('local', {
     successRedirect: '/',
     failureRedirect: '/login',
+    keepSessionInfo: true,
 }));
 
 
