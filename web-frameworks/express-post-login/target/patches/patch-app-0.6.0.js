--- app.js	2023-06-18 20:18:14
+++ app-0.6.0.js	2023-06-18 21:59:08
@@ -11,11 +11,7 @@
     resave: true,
     saveUninitialized: true}));
 
-// To prevent session fixation@0.5.3
-var fixation = require('express-session-fixation');
-app.use(fixation({}));
 
-
 const passport = require('passport');
 const LocalStrategy = require('passport-local').Strategy;
 
@@ -70,13 +66,11 @@
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
+    })(req,res,next);
 })
 
 app.post('/transfer', csrfProtection, (req, res, next) => {
@@ -97,8 +91,8 @@
         if (err) { return next(err); }
         res.redirect('/');
       });
-    req.session.destroy();
-    res.redirect('/');
+    // req.session.destroy();
+    // res.redirect('/');
 })
 
 app.listen(3000);
