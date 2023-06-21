--- app.js	2023-06-18 19:37:10
+++ app-0.6.0-keepSessionInfo.js	2023-06-18 21:59:46
@@ -11,11 +11,6 @@
     resave: true,
     saveUninitialized: true}));
 
-// To prevent session fixation@0.5.3
-var fixation = require('express-session-fixation');
-app.use(fixation({}));
-
-
 const passport = require('passport');
 const LocalStrategy = require('passport-local').Strategy;
 
@@ -68,13 +63,12 @@
 })
 
 app.post('/login', (req, res, next) => {
-    // To prevent session fixation@0.5.3
-    req.resetSessionID().then(function() {
-        passport.authenticate('local',{
-            successRedirect: '/',
-            failureRedirect: '/login',
-        })(req,res,next);
-    })
+    // Usage with 0.6.0
+    passport.authenticate('local',{
+        successRedirect: '/',
+        failureRedirect: '/login',
+        keepSessionInfo: true
+    })(req,res,next);
 })
 
 app.post('/transfer', csrfProtection, (req, res, next) => {
@@ -95,8 +89,8 @@
         if (err) { return next(err); }
         res.redirect('/');
       });
-    req.session.destroy();
-    res.redirect('/');
+    // req.session.destroy();
+    // res.redirect('/');
 })
 
 app.listen(3000);
